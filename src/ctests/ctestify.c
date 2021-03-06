
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>
#include "ctestify.h"


void test_results_initialize(test_results *results, char *errfilename)
{
    FILE *fp = fopen(errfilename, "w");
    if (fp == NULL) {
        fprintf(stderr, "Unable to open '%s'\n", errfilename);
        exit(-1);
    }
    results->num_assertions = 0;
    results->num_failed = 0;
    results->errfilename = errfilename;
    results->errfile = fp;
}


void test_results_finalize(test_results *results)
{
    fclose(results->errfile);
    if (results->num_failed == 0) {
        // No errors reported, so remove the log file.
        remove(results->errfilename);
    }
}


void test_results_fprint_summary(FILE *out, test_results *results, char *label)
{
    if (label != NULL) {
        fprintf(out, "%-24s ", label);
    }
    fprintf(out, "Assertions: %4d    Failures: %5d",
            results->num_assertions, results->num_failed);
    if (results->num_failed > 0) {
        fprintf(out, " ***");
    }
    fprintf(out, "\n");
}


void test_results_print_summary(test_results *results, char *label)
{
    test_results_fprint_summary(stderr, results, label);
}


void _assert_true(test_results *results, int value, char *msg, char *filename, int linenumber)
{
    results->num_assertions += 1;
    if (!value) {
        fprintf(results->errfile, "Assertion failed: %s:%d  %s\n", filename, linenumber, msg);
        fprintf(results->errfile, "... value is not true: %d\n", value);
        fflush(results->errfile);
        results->num_failed += 1;
    }
}


void _assert_equal_pointer(test_results *results, void *value1, void *value2,
                           char *msg, char *filename, int linenumber)
{
    results->num_assertions += 1;
    if (value1 != value2) {
        fprintf(results->errfile, "Assertion failed: %s:%d  %s\n", filename, linenumber, msg);
        fprintf(results->errfile, "... pointer values not equal\n");
        fflush(results->errfile);
        results->num_failed += 1;
    }
}


void _assert_equal_str(test_results *results, char *value1, char *value2,
                       char *msg, char *filename, int linenumber)
{
    results->num_assertions += 1;
    if (strcmp(value1, value2) != 0) {
        fprintf(results->errfile, "Assertion failed: %s:%d  %s\n", filename, linenumber, msg);
        fprintf(results->errfile, "... str values not equal: '%s' and '%s'\n", value1, value2);
        fflush(results->errfile);
        results->num_failed += 1;
    }
}

void _assert_equal_mem(test_results *results, char *value1, char *value2, size_t n,
                       char *msg, char *filename, int linenumber)
{
    results->num_assertions += 1;
    if (memcmp(value1, value2, n) != 0) {
        fprintf(results->errfile, "Assertion failed: %s:%d  %s\n", filename, linenumber, msg);
        fprintf(results->errfile, "... memory contents not equal, found:");
        for (size_t i = 0; i < n; ++i) {
            fprintf(results->errfile, " %02x", *(value1 + i));
        }
        fprintf(results->errfile, "\n");
        fflush(results->errfile);
        results->num_failed += 1;
    }
}


void _assert_equal_char32(test_results *results, char32_t *value1, char32_t *value2,
                          char *msg, char *filename, int linenumber)
{
    bool fail = false;
    results->num_assertions += 1;
    while ((*value1 != 0) && (*value2 != 0)) {
        if (*value1 != *value2) {
            fail = true;
            break;
        }
    }
    if (fail) {
        fprintf(results->errfile, "Assertion failed: %s:%d  %s\n", filename, linenumber, msg);
        fprintf(results->errfile, "... char32 values not equal: '%u' and '%u'\n", *value1, *value2);
        fflush(results->errfile);
        results->num_failed += 1;
    }
}
