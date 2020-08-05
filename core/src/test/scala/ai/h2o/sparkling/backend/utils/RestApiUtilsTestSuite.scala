/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package ai.h2o.sparkling.backend.utils

import ai.h2o.sparkling.SharedH2OTestContext
import ai.h2o.sparkling.backend.exceptions.RestApiCommunicationException
import ai.h2o.sparkling.extensions.rest.api.Paths
import org.apache.spark.sql.SparkSession
import org.junit.runner.RunWith
import org.scalatestplus.junit.JUnitRunner
import org.scalatest.{FunSuite, Matchers}
import water.parser.ParseTime

@RunWith(classOf[JUnitRunner])
class RestApiUtilsTestSuite extends FunSuite with Matchers with SharedH2OTestContext {

  override def createSparkSession(): SparkSession = sparkSession("local[*]")

  test("Error message from unsuccessful call contains information from the server") {
    val conf = hc.getConf
    val endpoint = RestApiUtils.getClusterEndpoint(conf)

    val caught = intercept[RestApiCommunicationException](RestApiUtils.update(endpoint, Paths.CHUNK, conf))

    assert(caught.getMessage.contains("Cannot find value for the parameter 'frame_name'"))
  }

  test("Set America/Los_Angeles timezone to H2O cluster") {
    testSettingTimezoneToH2OCluster("America/Los_Angeles")
  }

  test("Set Europe/Prague timezone to H2O cluster") {
    testSettingTimezoneToH2OCluster("Europe/Prague")
  }

  test("Set UTC timezone to H2O cluster") {
    testSettingTimezoneToH2OCluster("UTC")
  }

  private def testSettingTimezoneToH2OCluster(timezone: String): Unit = {
    val conf = hc.getConf
    println(ParseTime.listTimezones)
    RestApiUtils.setTimeZone(conf, timezone)
    val result = RestApiUtils.getTimeZone(conf)
    result shouldEqual timezone
  }
}
