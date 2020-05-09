import argparse
from batch_jobs import job

def get_parser():
    parser = argparse.ArgumentParser(description="Job Manager")
    parser.add_argument('--job', type=str, required=True, help='generate_glb|...')
    parser.add_argument('--spu_id', type=str, help='id of spu, job must be generate_glb')
    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    job.main(args)
