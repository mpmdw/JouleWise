/* Conservative, allocation-free plist byte scanner. No XML tree, no decisions.
 * Every value is grammar-checked, including ignored subtrees. Unhandled XML,
 * encodings, entities, scalar forms, depth or shapes return 0 for plistlib.
 * Output is offsets into exactly the caller's frame, never borrowed pointers.
 */
#include <stddef.h>
#include <string.h>
#include <ctype.h>

typedef struct { size_t start, end; } Span;
typedef struct { const unsigned char *s; size_t n, p; Span *out; } Scan;

static void ws(Scan *s) {
    while (s->p < s->n && (s->s[s->p]==' ' || s->s[s->p]=='\t' ||
           s->s[s->p]=='\r' || s->s[s->p]=='\n')) s->p++;
}
static int eat(Scan *s, const char *text) {
    size_t n = strlen(text);
    if (s->p+n>s->n || memcmp(s->s+s->p,text,n)) return 0;
    s->p+=n; return 1;
}
static int text(Scan *s, const char *close, size_t *a, size_t *b) {
    *a=s->p;
    const unsigned char *end=memchr(s->s+s->p,'<',s->n-s->p);
    if(!end) return 0;
    *b=(size_t)(end-s->s);
    unsigned int bad=0;
    for(size_t i=*a;i<*b;i++) {
        unsigned char c=s->s[i];
        bad |= c=='&' || c>=127 || (c<32 && c!='\t' && c!='\r' && c!='\n');
        if(c=='>' && i>=2 && s->s[i-1]==']' && s->s[i-2]==']') bad=1;
    }
    if(bad) return 0;
    s->p=*b;
    return eat(s,close);
}
static int equal(Scan *s,size_t a,size_t b,const char *key) {
    return b-a==strlen(key) && !memcmp(s->s+a,key,b-a);
}
static int number(Scan *s, size_t a, size_t b, int real) {
    if(!real && b-a>4000) return 0; /* Let Python own its configured digit limit. */
    size_t p=a;
    if(p<b && (s->s[p]=='-' || s->s[p]=='+')) p++;
    size_t before=p;
    while(p<b && s->s[p]>='0' && s->s[p]<='9') p++;
    int digits=p>before;
    if(real && p<b && s->s[p]=='.') {
        before=++p;
        while(p<b && s->s[p]>='0' && s->s[p]<='9') p++;
        digits |= p>before;
    }
    if(!digits) return 0;
    if(real && p<b && (s->s[p]=='e' || s->s[p]=='E')) {
        p++;
        if(p<b && (s->s[p]=='-' || s->s[p]=='+')) p++;
        before=p;
        while(p<b && s->s[p]>='0' && s->s[p]<='9') p++;
        if(p==before) return 0;
    }
    return p==b;
}
static int date(Scan *s,size_t a,size_t b) {
    if(b-a!=20) return 0;
    const unsigned char *p=s->s+a;
    for(int i=0;i<20;i++) {
        char c=i==4||i==7?'-':i==10?'T':i==13||i==16?':':i==19?'Z':0;
        if(c ? p[i]!=c : p[i]<'0'||p[i]>'9') return 0;
    }
    int year=(p[0]-'0')*1000+(p[1]-'0')*100+(p[2]-'0')*10+p[3]-'0';
    int month=(p[5]-'0')*10+p[6]-'0', day=(p[8]-'0')*10+p[9]-'0';
    static const int days[]={0,31,28,31,30,31,30,31,31,30,31,30,31};
    return year>0 && month>0 && month<=12 && day>0 &&
        day<=days[month]+(month==2 && year%4==0 && (year%100!=0 || year%400==0)) &&
        (p[11]-'0')*10+p[12]-'0'<24 && (p[14]-'0')*10+p[15]-'0'<60 &&
        (p[17]-'0')*10+p[18]-'0'<60;
}
static int value(Scan *,int,int);
static int dict(Scan *s,int depth,int context) {
    for(;;) {
        ws(s);
        if(eat(s,"</dict>")) return 1;
        size_t a,b;
        if(!eat(s,"<key>") || !text(s,"</key>",&a,&b)) return 0;
        ws(s);
        int slot=0, child=0;
        if(context==1) {
            if(equal(s,a,b,"elapsed_ns")) slot=1;
            else if(equal(s,a,b,"timestamp")) slot=2;
            else if(equal(s,a,b,"thermal_pressure")) slot=3;
            else if(equal(s,a,b,"processor")) {
                s->out[0]=(Span){1,1};
                child=2;
                for(int i=4;i<=9;i++) s->out[i]=(Span){0,0};
            } else if(equal(s,a,b,"gpu")) {
                child=3;
                memset(s->out+10,0,(396-10)*sizeof(Span));
            }
        } else if(context==2) {
            const char *keys[]={"cpu_power","gpu_power","ane_power","cpu_energy","gpu_energy","ane_energy"};
            for(int i=0;i<6;i++) if(equal(s,a,b,keys[i])) slot=4+i;
        } else if(context==3 && equal(s,a,b,"dvfm_states")) {
            child=4; slot=10;
            memset(s->out+11,0,(396-11)*sizeof(Span));
        } else if(context==5) {
            const char *keys[]={"freq","used_ns","used_ratio"};
            for(int i=0;i<3;i++) if(equal(s,a,b,keys[i])) slot=12+3*(s->out[11].start-1)+i;
        }
        size_t start=s->p;
        if(!value(s,depth+1,child)) return 0;
        if(slot) s->out[slot]=(Span){start,s->p};
    }
}
static int value(Scan *s,int depth,int context) {
    if(depth>64 || s->p+2>s->n || s->s[s->p]!='<') return 0;
    unsigned char tag=s->s[s->p+1];
    if(tag=='d' && eat(s,"<dict>")) return dict(s,depth,context);
    if(context && context!=4) return 0;
    if(tag=='d' && eat(s,"<dict/>")) return 1;
    if(tag=='a' && eat(s,"<array>")) {
        for(;;) {
            ws(s);
            if(eat(s,"</array>")) return 1;
            if(context==4 && ++s->out[11].start>128) return 0;
            if(!value(s,depth+1,context==4?5:0)) return 0;
        }
    }
    if(tag=='a' && eat(s,"<array/>") || tag=='t' && eat(s,"<true/>") ||
       tag=='f' && eat(s,"<false/>") || tag=='s' && eat(s,"<string/>")) return 1;
    size_t a,b;
    if(tag=='s' && eat(s,"<string>")) return text(s,"</string>",&a,&b);
    if(tag=='i' && eat(s,"<integer>")) return text(s,"</integer>",&a,&b) && number(s,a,b,0);
    if(tag=='r' && eat(s,"<real>")) return text(s,"</real>",&a,&b) && number(s,a,b,1);
    if(tag=='d' && eat(s,"<date>")) return text(s,"</date>",&a,&b) && date(s,a,b);
    return 0;
}

int jw_scan(const unsigned char *frame,size_t n,Span *out) {
    memset(out,0,396*sizeof(Span));
    Scan s={frame,n,0,out};
    ws(&s);
    eat(&s,"<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
    ws(&s);
    eat(&s,"<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">");
    ws(&s);
    if(!eat(&s,"<plist version=\"1.0\">")) return 0;
    ws(&s);
    if(!eat(&s,"<dict>") || !dict(&s,0,1)) return 0;
    ws(&s);
    if(!eat(&s,"</plist>")) return 0;
    ws(&s);
    return s.p==s.n;
}
