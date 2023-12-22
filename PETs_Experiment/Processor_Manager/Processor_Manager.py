from PETs_Experiment.Preprocessor.Missingist_Drop import Missingist_Drop
from PETs_Experiment.Preprocessor.Missingist_Mean import Missingist_Mean
from PETs_Experiment.Preprocessor.Missingist_Median import Missingist_Median
from PETs_Experiment.Preprocessor.Missingist_Simple import Missingist_Simple

from PETs_Experiment.Preprocessor.Outlierist_IQR import Outlierist_IQR
from PETs_Experiment.Preprocessor.Outlierist_IsolationForest import Outlierist_IsolationForest
from PETs_Experiment.Preprocessor.Outlierist_LOF import Outlierist_LOF
from PETs_Experiment.Preprocessor.Outlierist_Zscore import Outlierist_Zscore

from PETs_Experiment.Preprocessor.Encoder_Label import Encoder_Label
from PETs_Experiment.Preprocessor.Encoder_Uniform import Encoder_Uniform

from PETs_Experiment.Preprocessor.Scaler_MinMax import Scaler_MinMax
from PETs_Experiment.Preprocessor.Scaler_Standard import Scaler_Standard
from PETs_Experiment.Preprocessor.Scaler_ZeroCenter import Scaler_ZeroCenter

class Processor_Manager:

    # object datatype indicates the unusual data,
    # radical actions will be taken in processing procedure

    _DEFAULT_MISSINGIST = {'numerical': Missingist_Mean, 
                           'categorical': Missingist_Drop,
                           'datetime': Missingist_Drop,
                           'object': Missingist_Drop}
    
    # TODO - add LOF and Isolation Forest as global config to outlierist
    
    _DEFAULT_OUTLIERIST = {'numerical': Outlierist_IQR,
                           'categorical': None,
                           'datatime': Outlierist_IQR,
                           'object': None}
    
    _DEFAULT_ENCODER = {'numerical': None,
                        'categorical': Encoder_Uniform,
                        'datetime': None,
                        'object': Encoder_Uniform}
    
    _DEFAULT_SCALER = {'numerical': Scaler_Standard,
                       'categorical': None,
                       'datetime': Scaler_Standard,
                       'object': None}
    


    def __init__(self, metadata) -> None:
        self.metadata = metadata
        self.config = None

    def _check_metadata_valid():
        pass

    def _check_config_valid():
        pass

    def get_config():
        pass

    def set_config():
        pass

    def fit():
        pass

    def transform():
        pass

    def inverse_transform():
        pass

    def get_processor():
        pass

