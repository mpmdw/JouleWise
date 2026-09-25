#include <stdint.h>
#include <math.h>
static uint64_t step(uint64_t *s){uint64_t x=*s;x^=x>>12;x^=x<<25;x^=x>>27;*s=x;return x*2685821657736338717ULL;}
static double variance(const double *x,int n){double a=0,b=0;for(int i=0;i<n;i++){a+=x[i];b+=x[i]*x[i];}return (b-a*a/n)/(n-1);}
double perm_p(const double *x,int no,int nn,int reps,uint64_t seed){
 double pool[128],total=0,sq=0; int n=no+nn,hits=0;double observed=variance(x+no,nn)/variance(x,no);
 for(int j=0;j<n;j++){pool[j]=x[j];total+=x[j];sq+=x[j]*x[j];}
 for(int r=0;r<reps;r++){
   double a=0,b=0;
   for(int j=0;j<nn;j++){int q=j+(step(&seed)%(n-j));double t=pool[j];pool[j]=pool[q];pool[q]=t;a+=pool[j];b+=pool[j]*pool[j];}
   double vn=(b-a*a/nn)/(nn-1), vo=(sq-b-(total-a)*(total-a)/no)/(no-1);
   if(vn/vo >= observed*exp(-1e-12))hits++;
 }
 return (hits+1.0)/(reps+1.0);
}
