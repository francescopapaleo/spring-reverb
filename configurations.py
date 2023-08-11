from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser(description='Train a TCN model on the plate-spring dataset')

    # Paths
    parser.add_argument('--datadir', type=str, default='../datasets/egfxset/', help='Path (rel) to the dataset ')
    parser.add_argument('--audiodir', type=str, default='audio/processed/', help='Path (rel) to the audio files')
    parser.add_argument('--logdir', type=str, default='results/', help='Path (rel) to  the log directory')
    parser.add_argument('--plotsdir', type=str, default='results/plots', help='Path (rel) to the plot directory')
    parser.add_argument('--checkpoint_path', type=str, default='results/checkpoints/', help='Path (rel) to checkpoint to load')
    parser.add_argument('--input', type=str, default=None, help='Path (rel) to audio file to process')

    # Model
    parser.add_argument('--config', type=str, default='TCN_Baseline', help='The configuration to use')
    parser.add_argument('--device', type=str, default=None, help='set device to run the model on')
    parser.add_argument('--sample_rate', type=int, default=48000, help='sample rate of the audio')    
    parser.add_argument('--n_epochs', type=int, default=25, help='the total number of epochs')
    parser.add_argument('--batch_size', type=int, default=4, help='batch size')
    parser.add_argument('--lr', type=float, default=0.0001, help='learning rate')
    # parser.add_argument('--crop', type=int, default=240000, help='crop size')
        
    # Inference
    parser.add_argument('--max_length', type=float, default=None, help='maximum length of the output audio')
    parser.add_argument('--stereo', action='store_false', help='flag to indicate if the audio is stereo or mono')
    parser.add_argument('--tail', action='store_true', help='flag to indicate if tail padding is required')
    parser.add_argument('--width', type=float, default=100, help='width parameter for the model')
    parser.add_argument('--c0', type=float, default=0, help='c0 parameter for the model')
    parser.add_argument('--c1', type=float, default=0, help='c1 parameter for the model')
    parser.add_argument('--gain_dB', type=float, default=-18.0, help='gain in dB for the model')
    parser.add_argument('--mix', type=float, default=100, help='mix parameter for the model')
    
    # Measurements
    parser.add_argument("--duration", type=float, default=0.5, help="duration in seconds")
    parser.add_argument("--mode", type=str, choices=['ir', 'tf'], default='ir', help="Mode to run: 'ir' for impulse response or 'tf' for transfer function")
    
    return parser.parse_args()

configs = [{
    'conf_name': 'TCN-BL',
    'model_type': 'TCN',
    'n_channels': 32,
    'dilation': 10,
    'n_blocks': 5,
    'kernel_size': 9,
    'cond_dim': 2,
    },
    {
    'conf_name': 'WN-8-10-2',
    'model_type': 'WaveNet',
    'n_channels': 8,
    'dilation': 10,
    'num_repeat': 2,
    'kernel_size': 5,
    },
    {
    'conf_name': 'LSTM-96',
    'model_type': 'LSTM',
    'input_size': 1,
    'output_size': 1,
    'hidden_size': 96,
    'num_layers': 1,
    },
    {
    'conf_name': 'LSTM-96-skip',
    'model_type': 'LSTMskip',
    'input_size': 1,
    'output_size': 1,
    'hidden_size': 96,
    'num_layers': 1,
    },
    ]
