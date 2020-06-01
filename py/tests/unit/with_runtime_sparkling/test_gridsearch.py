# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
from pyspark.ml import Pipeline, PipelineModel
from pyspark.mllib.linalg import *
from pyspark.sql.types import *
from pysparkling.ml import H2OGridSearch, H2OGBM, H2OXGBoost, H2ODeepLearning, H2OGLM, H2ODRF

from tests.unit.with_runtime_sparkling.algo_test_utils import *


def testParamsPassedByConstructor():
    # Skipping testing of algo option as we don't generate equal algo
    assertParamsViaConstructor("H2OGridSearch", ["algo"])


def testParamsPassedBySetters():
    # Skipping testing of algo option as we don't generate equal algo
    assertParamsViaSetters("H2OGridSearch", ["algo"])


def gridSearchTester(algo, prostateDataset):
    grid = H2OGridSearch(hyperParameters={"seed": [1, 2, 3]}, algo=algo.setLabelCol("AGE").setSplitRatio(0.8),
                         strategy="RandomDiscrete", maxModels=3, maxRuntimeSecs=60, selectBestModelBy="RMSE")

    pipeline = Pipeline(stages=[grid])
    pipeline.write().overwrite().save("file://" + os.path.abspath("build/grid_pipeline"))
    loadedPipeline = Pipeline.load("file://" + os.path.abspath("build/grid_pipeline"))
    model = loadedPipeline.fit(prostateDataset)

    model.write().overwrite().save("file://" + os.path.abspath("build/grid_pipeline_model"))
    loadedModel = PipelineModel.load("file://" + os.path.abspath("build/grid_pipeline_model"))

    loadedModel.transform(prostateDataset).count()


def testPipelineSerializationGBM(prostateDataset):
    gridSearchTester(H2OGBM(), prostateDataset)


def testPipelineSerializationGLM(prostateDataset):
    gridSearchTester(H2OGLM(), prostateDataset)


def testPipelineSerializationDeepLearning(prostateDataset):
    gridSearchTester(H2ODeepLearning(), prostateDataset)


def testPipelineSerializationXGBoost(prostateDataset):
    gridSearchTester(H2OXGBoost(), prostateDataset)

def testPipelineSerializationDRF(prostateDataset):
    gridSearchTester(H2ODRF(), prostateDataset)


def testGetGridModelsParams(prostateDataset):
    grid = H2OGridSearch(hyperParameters={"seed": [1, 2, 3]}, algo=H2OGBM(labelCol="AGE", splitRatio=0.8),
                         strategy="RandomDiscrete", maxModels=3, maxRuntimeSecs=60, selectBestModelBy="RMSE")

    grid.fit(prostateDataset)
    params = grid.getGridModelsParams()
    assert params.count() == 3
    assert params.columns == ['MOJO Model ID', 'seed']
    params.collect() # try materializing

def testGetGridModelsNoParams(prostateDataset):
    grid = H2OGridSearch(algo=H2OGBM(labelCol="AGE", splitRatio=0.8), strategy="RandomDiscrete", maxModels=3,
                         maxRuntimeSecs=60, selectBestModelBy="RMSE")

    grid.fit(prostateDataset)
    params = grid.getGridModelsParams()
    assert params.count() == 1
    assert params.columns == ['MOJO Model ID']
    params.collect() # try materializing

def testGetGridModelsMetrics(prostateDataset):
    grid = H2OGridSearch(hyperParameters={"seed": [1, 2, 3]}, algo=H2OGBM(labelCol="AGE", splitRatio=0.8),
                         strategy="RandomDiscrete", maxModels=3, maxRuntimeSecs=60, selectBestModelBy="RMSE")

    grid.fit(prostateDataset)
    metrics = grid.getGridModelsMetrics()
    assert metrics.count() == 3
    assert metrics.columns == ['MOJO Model ID', 'MSE', 'MeanResidualDeviance', 'R2', 'RMSE']
    metrics.collect() # try materializing

def testGetGridModels(prostateDataset):
    grid = H2OGridSearch(hyperParameters={"seed": [1, 2, 3]}, algo=H2OGBM(splitRatio=0.8, labelCol="AGE"),
                         strategy="RandomDiscrete", maxModels=3, maxRuntimeSecs=60, selectBestModelBy="RMSE")

    grid.fit(prostateDataset)
    models = grid.getGridModels()
    assert len(models) == 3

def testGetAlgoViaConstructor():
    # SW-2276, 3rd call of getAlgo failed
    grid = H2OGridSearch(hyperParameters={"seed": [1, 2, 3]}, algo=H2OGBM(labelCol="AGE", ntrees=100, splitRatio=0.8),
                         strategy="RandomDiscrete", maxModels=3, maxRuntimeSecs=60, selectBestModelBy="RMSE")
    grid.getAlgo()
    grid.getAlgo()
    assert grid.getAlgo().getNtrees() == 100

def testGetAlgoViaSetter():
    # SW-2276, 3rd call of getAlgo failed
    grid = H2OGridSearch(hyperParameters={"seed": [1, 2, 3]}, strategy="RandomDiscrete",
                         maxModels=3, maxRuntimeSecs=60, selectBestModelBy="RMSE")
    grid.setAlgo(H2OGBM().setNtrees(100).setLabelCol("AGE").setSplitRatio(0.8))
    grid.getAlgo()
    grid.getAlgo()
    assert grid.getAlgo().getNtrees() == 100
