#!/usr/bin/env bash

# Current dir
TOPDIR=$(cd "$(dirname "$0")/.."; pwd)

source "$TOPDIR/bin/sparkling-env.sh"
# Java check
checkJava
# Verify there is Spark installation
checkSparkHome
# Verify if correct Spark version is used
checkSparkVersion
# Check sparkling water assembly Jar exists
checkPyZipExists
# Check existence of dependant Python packages
checkPythonPackages

SCRIPT_MASTER=${MASTER:-"$DEFAULT_MASTER"}
SCRIPT_DEPLOY_MODE="cluster"
SCRIPT_DEPLOY_MODE=${DEPLOY_MODE:-"client"}
SCRIPT_DRIVER_MEMORY=${DRIVER_MEMORY:-$DEFAULT_DRIVER_MEMORY}
SCRIPT_H2O_SYS_OPS=${H2O_SYS_OPS:-""}

echo "---------"
echo "  Using master    (MASTER)       : $SCRIPT_MASTER"
echo "  Deploy mode     (DEPLOY_MODE)  : $SCRIPT_DEPLOY_MODE"
echo "  Driver memory   (DRIVER_MEMORY): $SCRIPT_DRIVER_MEMORY"
echo "  H2O JVM options (H2O_SYS_OPS)  : $SCRIPT_H2O_SYS_OPS"
echo "---------"
export SPARK_PRINT_LAUNCH_COMMAND=1
VERBOSE=--verbose

if [ -f "$SPARK_HOME/conf/spark-defaults.conf" ]; then
    EXTRA_DRIVER_PROPS=$(grep "^spark.driver.extraJavaOptions" "$SPARK_HOME"/conf/spark-defaults.conf 2>/dev/null | sed -e 's/spark.driver.extraJavaOptions//' )
fi

VERBOSE=
spark-submit \
--master "$SCRIPT_MASTER" \
--driver-memory "$SCRIPT_DRIVER_MEMORY" \
--driver-java-options "$SCRIPT_H2O_SYS_OPS" \
--deploy-mode "$SCRIPT_DEPLOY_MODE" \
--py-files "$PY_ZIP_FILE" \
--conf spark.driver.extraJavaOptions="$EXTRA_DRIVER_PROPS" \
$VERBOSE \
"$@"
