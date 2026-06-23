Rem Copyright (c) 1998, 2008, Oracle. All rights reserved.
Rem
Rem    NAME
Rem      utlrcmp.sql - Utility package for dependency-based recompilation
Rem                    of invalid objects sequentially or in parallel.
Rem
Rem    DESCRIPTION
Rem      This script provides a packaged interface to recompile invalid
Rem      PL/SQL modules, Java classes, indextypes and operators in a
Rem      database sequentially or in parallel.
Rem
Rem      This script is particularly useful after a major-version upgrade.
Rem      A major-version upgrade typically invalidates all PL/SQL and Java
Rem      objects. Although invalid objects are recompiled automatically on
Rem      use, it is useful to run this script ahead of time (e.g. as one of
Rem      the last steps in your migration), since this will either eliminate
Rem      or minimize subsequent latencies caused due to on-demand automatic
Rem      recompilation at runtime.
Rem
Rem   PARALLELISM AND PERFORMANCE
Rem      Parallel recompilation can exploit multiple CPUs to reduce the time
Rem      taken to recompile invalid objects. The degree of parallelism is
Rem      specified by the first argument to UTL_RECOMP.RECOMP_PARALLEL().
Rem      If the specified degree of parallelism is NULL, 0, or negative,
Rem      RECOMP_PARALLEL computes a default degree of parallelism as
Rem      the product of Oracle parameters "cpu_count" and
Rem      "parallel_threads_per_cpu". On a Real Application Clusters
Rem      installation, the degree of parallelism is the sum of individual
Rem      settings on each node in the cluster.
Rem
Rem      Please note that the process of recompiling an invalid
Rem      object writes a significant amount of data to system tables and is
Rem      fairly I/O intensive. A slow disk system may be a significant
Rem      bottleneck and limit speedups available from a higher degree of
Rem      parallelism.
Rem
Rem   EXAMPLES
Rem      1. Recompile all objects sequentially:
Rem             execute utl_recomp.recomp_serial();
Rem
Rem      2. Recompile objects in schema SCOTT sequentially:
Rem             execute utl_recomp.recomp_serial('SCOTT');
Rem
Rem      3. Recompile all objects using 4 parallel threads:
Rem             execute utl_recomp.recomp_parallel(4);
Rem
Rem      4. Recompile objects in schema JOE using the default degree
Rem         of parallelism.
Rem             execute utl_recomp.recomp_parallel(NULL, 'JOE');
Rem
Rem   NOTES
Rem      * You must be connected AS SYSDBA using SQL*PLUS to run this script.
Rem      * This script uses the job queue for parallel recompilation.
Rem      * This script expects the following packages to have been created with
Rem        VALID status:
Rem          STANDARD       (standard.sql)
Rem          DBMS_STANDARD  (dbmsstdx.sql)
Rem      * There should be no other DDL on the database while running
Rem        entries in this package. Not following this recommendation may
Rem        lead to deadlocks.

Rem
Rem   MODIFIED   (MM/DD/YY)
Rem    sylin      02/19/08 - Enable recomp_parallel for TimesTen
Rem    sylin      12/05/07 - TimesTen support
Rem    gviswana   03/07/07 - 5896174: Recompile ADTs first
Rem    jmuller    04/21/05 - Separate spec and body
Rem    gviswana   03/14/05 - 4238924: Catch invalidate exceptions
Rem    gviswana   03/08/05 - 4201450,4225325: Abnormal termination
Rem    gviswana   02/07/05 - 3647039: Recompile objects with errors
Rem    gviswana   01/05/05 - 4105056: Compile seq objects correctly
Rem    gviswana   11/11/04 - 3566151: Analyze tables after insertion
Rem    gviswana   09/09/04 - Auto tuning: RAC and DBMS_SCHEDULER
Rem    ciyer      03/09/04 - allow recompiles of specs only
Rem    gviswana   07/26/04 - Make sequence NOCACHE to avoid skips
Rem    ciyer      07/06/04 - bug 3739622: avoid objects in the recycle bin
Rem    ciyer      01/21/04 - performance improvements
Rem    gviswana   12/15/03 - 3320292: Avoid validating generated types
Rem    gviswana   10/27/03 - 3211722: Push call for validation
Rem    gviswana   06/29/03 - 2814808: Wait for parallel jobs to complete
Rem    gviswana   07/21/03 - 2989859: Topological sort for serial recomp
Rem    gviswana   06/02/03 - Remove jobs when done
Rem    twtong     06/06/03 - bug-2988266
Rem    gviswana   04/10/03 - Use dbms_utility.validate
Rem    gviswana   03/18/03 - 2849370: Fix premature termination
Rem    twtong     04/08/03 - fix bug-2874778
Rem    weiwang    01/14/03 - validate queues and rules engine objects
Rem    gviswana   10/28/02 - Deferred synonym translation
Rem    rburns     08/21/02 - add materialized views
Rem    gviswana   06/25/02 - Add documentation
Rem    wxli       01/18/02 - recomp_parallel including java parallel
Rem    spsundar   12/20/01 - validate indexes (domain) too
Rem    gviswana   12/06/01 - Wrap DROP TABLE statements
Rem    gviswana   10/12/01 - Fold in changes from utlrp.sql
Rem    gviswana   06/03/01 - Merged gviswana_utl_recomp_1
Rem    gviswana   05/29/01 - Creation from utlrp.sql
Rem

Rem ===========================================================================
Rem BEGIN utlrcmp.sql
Rem ===========================================================================

CREATE OR REPLACE PACKAGE utl_recomp IS

$if utl_ident.is_oracle_server <> TRUE and
    utl_ident.is_timesten <> TRUE $then
  $error 'utl_recomp is not supported in this environment' $end
$end

   COMPILE_LOG       CONSTANT PLS_INTEGER := 2;
   NO_REUSE_SETTINGS CONSTANT PLS_INTEGER := 4;
   RANDOM_ORDER      CONSTANT PLS_INTEGER := 8;
   REVERSE_ORDER     CONSTANT PLS_INTEGER := 16;
   SPECS_ONLY        CONSTANT PLS_INTEGER := 32;
   TYPES_ONLY        CONSTANT PLS_INTEGER := 64;

   PROCEDURE recomp_parallel(threads PLS_INTEGER := NULL,
                             schema  VARCHAR2    := NULL,
                             flags   PLS_INTEGER := 0);

   PROCEDURE recomp_serial(schema VARCHAR2 := NULL, flags PLS_INTEGER := 0);

$if utl_ident.is_oracle_server $then
   PROCEDURE parallel_slave(flags PLS_INTEGER);
$else

$end

END;
/
show errors;


Rem ===========================================================================
Rem END utlrcmp.sql
Rem ===========================================================================
