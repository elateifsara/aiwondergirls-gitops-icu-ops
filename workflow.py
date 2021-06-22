
from kfp import dsl
import mlrun
from mlrun.platforms import auto_mount


funcs = {}
DATASET = 'train_enc'
TST_DATASET = 'test_enc'
LABELS =  'diabetes_mellitus'

# Configure function resources and local settings
def init_functions(functions: dict, project=None, secrets=None):
    for f in functions.values():
        f.apply(auto_mount())

# Create a Kubeflow Pipelines pipeline
@dsl.pipeline(
    name="WidsDB2",
    description="This workflow implements the pipeline for data preprocessing, training model "
                "serving for Widsdb2 dataset \n"
                
)

def kfpipeline(source_url='store://raw_train_data', test_url='store://raw_test_data'):

    # Ingest the data set
    ingest = funcs['prep'].as_step(
        name="prep",
        handler='trdata_prep',
        inputs={'src': source_url},
        outputs=[DATASET])
    
     # Ingest the data set
    test = funcs['tstprep'].as_step(
        name="tstprep",
        handler='tstdata_prep',
        inputs={'src': test_url},
        outputs=[TST_DATASET])
    
        # Train a model   
    train = funcs["train-wids"].as_step(
        name="train-wids",
        params={"label_column": LABELS},
        inputs={"dataset": ingest.outputs[DATASET]},
        outputs=['model', 'test_set'])
  
     # Deploy the model as a serverless function
    deploy = funcs["lightgbm-serving"].deploy_step(
        models={f"{DATASET}_v1": train.outputs['model']})
   
   # test out new model server (via REST API calls)
    #tester = funcs["live_tester"].as_step(name='model-tester',
    #    params={'addr': deploy.outputs['endpoint'], 'model': f"{DATASET}:v1", 'label_column':LABELS},
    #   inputs={'table': train.outputs['test_set']})
    
    
    ## Run the inference with the serving function
