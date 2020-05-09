import bpy
import sys
from config_generate_glb.graphql import Graphql
import os
import configparser


class GenerateGLB(Graphql):
    def __init__(self, media_url, shop_url, download_dir, material_library_path, export_dir):
        super().__init__(media_url, shop_url, download_dir)
        self.material_library_path = material_library_path
        self.export_dir = export_dir

    # Get materials used by sku
    @staticmethod
    def get_sku_materials(sku_info):
        material = []
        for mesh, attribute_values in sku_info.items():
            material.append(attribute_values['material_name'])
        return list(set(material))

    # Get all materials used by spu
    def get_spu_materials(self, spu_info):
        materials = []
        for sku, sku_info in spu_info.items():
            for material in self.get_sku_materials(sku_info):
                if material not in materials:
                    materials.append(material)
        return materials

    # Generate a glb that contains materials used by spu and the model of the spu
    def generate_materials_glb(self, upload_ids, spu_used_materials):
        for upload_id in upload_ids:
            bpy.ops.wm.open_mainfile(filepath=self.material_library_path)
            for material in bpy.data.materials:
                if material.name not in spu_used_materials:
                    bpy.data.materials.remove(material)
            original_glb_path = os.path.join(self.download_dir, upload_id + '.glb')
            bpy.ops.import_scene.gltf(filepath=original_glb_path)
            bpy.data.objects['Material_Library'].hide_viewport = True
            export_glb_path = os.path.join(self.export_dir, upload_id + '_materials')
            bpy.ops.export_scene.gltf(filepath=export_glb_path, export_format="GLB")

    def run(self, spu_id):
        spu_info = self.process_spu(spu_id)
        upload_ids = self.download_glb(spu_id)
        spu_used_materials = self.get_spu_materials(spu_info)

        self.generate_materials_glb(upload_ids, spu_used_materials)

        for upload_id in upload_ids:
            file_path = os.path.join(self.export_dir, upload_id + '_materials.glb')  # 文件上传路径
            self.upload(file_path, upload_id)


if __name__ == '__main__':
    # read config file
    cf = configparser.ConfigParser()
    cf.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.ini"))
    media_url = cf.get("Graphql-Database", "media_url")
    shop_url = cf.get("Graphql-Database", "shop_url")
    download_dir = cf.get("Graphql-Database", "download_dir")
    material_library_path = cf.get("Blender", "material_library_path")
    export_dir = cf.get("Blender", "export_dir")

    task = GenerateGLB(media_url, shop_url, download_dir, material_library_path, export_dir)
    spu_id = sys.argv[-1]  # get the last parameter of command
    task.run(spu_id)
