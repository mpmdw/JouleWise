/* Darwin-only, fixed-operation root helper. No argv, files, or shell input.
 * Install root:wheel 0755 at /Library/PrivilegedHelperTools/joulewise-zero-ntp-frequency
 * beneath root-owned, non-writable directories. Never setuid.
 * Caller must prove no night running and network time OFF before invocation.
 */
#include <stdio.h>
#include <unistd.h>
#include <sys/timex.h>

int main(int argc, char **argv) {
    (void)argv;
    if (argc != 1) {
        fputs("no arguments accepted\n", stderr);
        return 2;
    }
    if (geteuid() != 0) {
        fputs("root required\n", stderr);
        return 2;
    }
    struct timex value = {0};
    value.modes = MOD_OFFSET | MOD_FREQUENCY;
    value.offset = 0;
    value.freq = 0;
    /* TIME_ERROR is a readable undisciplined clock, not a syscall failure. */
    if (ntp_adjtime(&value) == -1) {
        perror("ntp_adjtime zero");
        return 1;
    }
    struct timex after = {0};
    if (ntp_adjtime(&after) == -1) {
        perror("ntp_adjtime read-back");
        return 1;
    }
    printf("frequency_word_after=%ld\n", after.freq);
    return after.freq == 0 ? 0 : 1;
}
