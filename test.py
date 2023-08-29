import torch
import torchaudio
import torchaudio.functional as F
import auraloss
import os
from datetime import datetime
from torch.utils.tensorboard import SummaryWriter
from pathlib import Path

from src.egfxset import load_egfxset
from src.springset import load_springset
from src.helpers import select_device, load_model_checkpoint
from configurations import parse_args

def main():
    print("Testing model...")
    print(torchaudio.get_audio_backend())

    args = parse_args()
    torch.manual_seed(42)
    
    device = select_device(args.device)

    torch.backends.cudnn.deterministic = True
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
    torch.cuda.empty_cache()

    sample_rate = args.sample_rate
    bit_rate = args.bit_rate

    model, model_name, hparams, optimizer_state_dict, scheduler_state_dict, last_epoch, rf, params = load_model_checkpoint(device, args.checkpoint, args)
    
    batch_size = hparams['batch_size']
    n_epochs = hparams['n_epochs']
    lr = hparams['lr']

    # timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_dir = Path(args.logdir) / f"test/{model_name}"
    writer = SummaryWriter(log_dir=log_dir)
    
    # Load data
    if args.dataset == 'egfxset':
        _, _, test_loader = load_egfxset(args.datadir, args.batch_size)
    if args.dataset == 'springset':
        _, _, test_loader = load_springset(args.datadir, args.batch_size)
    
    mae = torch.nn.L1Loss()
    mse = torch.nn.MSELoss()
    esr = auraloss.time.ESRLoss()
    dc = auraloss.time.DCLoss()
    mrstft = auraloss.freq.MultiResolutionSTFTLoss()

    criterions = [mae, mse, esr, dc, mrstft]
    test_results = {"mae": [], "esr": [], "dc": [], "mrstft": []}

    num_batches = len(test_loader)
    rtf_list = []

    model.eval()
    with torch.no_grad():
        for step, (dry, wet) in enumerate(test_loader):
            start_time = datetime.now()
            
            input = dry
            target = wet            
            global_step = step + 1
            print(f"Batch {global_step}/{num_batches}")

            # move input and target to device
            input = input.to(device)                    
            target = target.to(device)

            # forward pass
            output = model(input)
            
            end_time = datetime.now()
            duration = end_time - start_time
            num_samples = input.size(-1) * batch_size
            lenght_in_seconds = num_samples / sample_rate
            rtf = duration.total_seconds() / lenght_in_seconds
            rtf_list.append(rtf)

            # Compute metrics means for current batch
            for metric, name in zip(criterions, test_results.keys()):
                batch_score = metric(output, target).item()
                test_results[name].append(batch_score)
            
            # Plot and save audios every n batches
            if step == num_batches - 1:

                output = torchaudio.functional.highpass_biquad(output, sample_rate, 20)
                target = torchaudio.functional.highpass_biquad(target, sample_rate, 20)

                input /= torch.max(torch.abs(input))
                target /= torch.max(torch.abs(target))                
                output /= torch.max(torch.abs(output))

                inp = input.view(-1).unsqueeze(0).cpu()
                tgt = target.view(-1).unsqueeze(0).cpu()
                out = output.view(-1).unsqueeze(0).cpu()

                sr_tag = sample_rate // 1000

                save_in = f"results/audio_batches/inp_{hparams['conf_name']}_{sr_tag}k.wav"
                torchaudio.save(save_in, inp, sample_rate=sample_rate)

                save_out = f"results/audio_batches/out_{hparams['conf_name']}_{sr_tag}k.wav"
                torchaudio.save(save_out, out, sample_rate=sample_rate)

                save_target = f"results/audio_batches/tgt_{hparams['conf_name']}_{sr_tag}k.wav"
                torchaudio.save(save_target, tgt, sample_rate=sample_rate)

    for name in test_results.keys():
        global_score = sum(test_results[name]) / len(test_results[name])
        writer.add_scalar(f'test/global_{name}', global_score, global_step)
    
    mean_test_results = {k: sum(v) / len(v) for k, v in test_results.items()}
    avg_rtf = sum(rtf_list) / len(rtf_list)
    mean_test_results['rtf'] = avg_rtf

    writer.add_hparams(hparams, mean_test_results)

    writer.flush()
    writer.close()

if __name__ == "__main__":
    main()
