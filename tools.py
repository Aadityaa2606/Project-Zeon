import random
import rsa


#generate a random session id
def genarate_session_id():
    return random.randint(0, 1500000)

def generate_keys():
    publickey,privatekey = rsa.newkeys(512)
    publickey = publickey.save_pkcs1().decode('utf-8').split("-----BEGIN RSA PUBLIC KEY-----")[1].split("-----END RSA PUBLIC KEY-----")[0].strip().replace("\n", " ")
    privatekey = privatekey.save_pkcs1().decode('utf-8').split("-----BEGIN RSA PRIVATE KEY-----")[1].split("-----END RSA PRIVATE KEY-----")[0].strip().replace("\n", " ")
    return publickey,privatekey