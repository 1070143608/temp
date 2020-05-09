import requests
import os
from . import dev
from core_msclients.aws.s3 import AWSS3Client
class NotExistIdException(Exception):
    pass

class Graphql:
    def __init__(self, media_url, shop_url, download_dir):
        self.media_url = media_url
        self.shop_url = shop_url
        self.download_dir = download_dir
        self.BUCKET = dev.BUCKET[0]
        self.aws_s3_jewel_build_client = AWSS3Client(s3_bucket_name=f"{dev.PROJECT}-{dev.MODE}-media-public",
                                                     s3_endpoint=self.BUCKET.get("AWS_S3_ENDPOINT_URL"),
                                                     s3_region=self.BUCKET.get("AWS_S3_REGION"),
                                                     s3_bucket_cdn=self.BUCKET.get("AWS_S3_BUCKET_CDN_HOST"),
                                                     mode='dev',
                                                     logger=dev.LOGGER)

    # Return a dictionary that contains corresponding upload ids and upload urls
    def query_spu_download_message(self, spu_id):
        print("Querying original GLBs of SPU...")
        data = {'query': '''{
              spu(id:"''' + spu_id + '''"){
            threedModel {
              edges {
                node {
                  id
                  uploadedModelMediamsFileId
                  uploadedModelMediamsFileIdInfo
                  displayModelMediamsFileId
                }
              }
            }
          }
        }'''}
        upload_response = requests.post(url=self.shop_url, data=data).json()
        dic = {}
        for node in upload_response['data']['spu']["threedModel"]["edges"]:
            node = node["node"]
            upload_id = node['id']
            for key, value in node['uploadedModelMediamsFileIdInfo'].items():
                upload_info = value[0]
                dic[upload_id] = upload_info["key"]
        print(len(dic))
        if len(dic) < 1:
            raise NotExistIdException('SUCH SPU ID NOT EXISTS!')
        print(len(dic), "Find original GLBs successfully")
        return dic

    # Download original glb files of spu, return
    def download_glb(self, spu_id):
        upload_ids = []
        for upload_id, upload_info in self.query_spu_download_message(spu_id).items():
            try:
                glb_path = os.path.join(self.download_dir, upload_id + '.glb')
                with open(glb_path, 'wb') as f:
                    self.aws_s3_jewel_build_client.download_fileobj(upload_info, f)
                upload_ids.append(upload_id)
            except:
                raise Exception(f"download error. error id: {upload_id}")
        return upload_ids

    # Query information of the spu
    def query_spu(self, spu_id):
        data = {'query': '''{
        products(spu_Id:"''' + spu_id + '''") {
          edges {
            node {
              id
              productSelectValues(modelMesh_Isnull:false){
                edges {
                  node {
                    modelMesh {
                        nameCode
                    }
                    selectValue{
                        value
                    }
                  }
                }
              }
            }
          }
        }
      }'''}
        response = requests.post(url=self.shop_url, data=data)
        if response.status_code == 200:
            return response
        else:
            raise Exception(f"Fail to query spu. status: {response.status_code}")

    # process spu information and return a dictionary that contains corresponding mesh and attribute value
    def process_spu(self, spu_id):
        data = self.query_spu(spu_id).json()
        if len(data["data"]["products"]["edges"]) < 1:
            raise Exception("Fail to find SPU")

        dic = {}
        for sku in data["data"]["products"]["edges"]:
            sku_id = sku["node"]["id"]
            dic[sku_id] = {}
            for node in sku["node"]["productSelectValues"]["edges"]:
                mesh = node["node"]
                mesh_name = mesh["modelMesh"]["nameCode"]
                if not dic[sku_id].get(mesh_name):
                    dic[sku_id][mesh_name] = {}
                attr_value = mesh["selectValue"]["value"]
                for key, value in attr_value.items():
                    dic[sku_id][mesh_name][key] = value
        return dic

    # Get authorization to upload file
    def get_media_upload_path(self):
        data = {'query': '''{
          resources(
            service: "shop", 
            attribute:"display_model_mediams_file_id",
            table:"shop_threed_spu_product_3d_models"
            ){
            edges{
              node{
                id
                attribute
                presignedPostUrl(count:1){
                  url
                  fields
                }
                mediaType {
                  type
                  mime
                  suffix
                }
                maxFilesize
                minFilesize
              }
            }
            serverStatus {
              code
              message
            }
          }
        }'''}
        media = requests.post(self.media_url, data=data)
        if media.status_code == 200:
            print("Successfully get authorization.")
        else:
            raise Exception(f"Fail to get authorization.status: {media.status_code}")
        response = media.json()
        fields = response['data']['resources']['edges'][0]['node']['presignedPostUrl'][0]['fields']
        key = fields['key']
        url = response['data']['resources']['edges'][0]['node']['presignedPostUrl'][0]['url']
        return fields, key, url

    # Bond uploaded file to spu
    def bond(self, upload_id, key):
        data = {'query': '''mutation{
            updateSpuProduct3dModel(input:{
             id:"''' + upload_id + '''",
             displayModelMediamsFileId:"''' + key + '''"
            }){
             serverStatus {
               code
               message
             }
            }
            }'''}
        shop = requests.post(self.shop_url, data=data)
        response = shop.json()
        status_code = response['data']['updateSpuProduct3dModel']['serverStatus']['code']
        if status_code == 200:
            print("Successfully bond file to spu.")
        else:
            raise Exception(f"Fail to bond.status: {shop.status_code}")

    # Get authorization, upload file and bond file to spu
    def upload(self, file_path, upload_id):
        fields, key, url = self.get_media_upload_path()
        body = fields
        file = open(file_path, 'rb')
        #files = {'file': file}
        try:
            self.aws_s3_jewel_build_client.upload_fileobj(data=file, filekey=key)
        #upload = requests.post(url, data=body, files=files)
        except:
            raise Exception(f"Fail to upload ")
        self.bond(upload_id, key)
