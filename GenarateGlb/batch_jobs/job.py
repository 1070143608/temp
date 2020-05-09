from .base import BaseJob
import subprocess

class GlbGenerator(BaseJob):
    required_args = [ "job", "spu_id"]

    def run(self):
        subprocess.run(["blender", "-b", "-P", "/srv/jewel-batch-jobs-gpu/GenarateGlb/generate_glb.py", "--", str(self.args.spu_id)])

def main(args):
    if args.job == "generate_glb":
        GlbGenerator(args).run()