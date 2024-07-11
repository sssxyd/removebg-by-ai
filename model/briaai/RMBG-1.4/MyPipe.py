import torch, os
import torch.nn.functional as F
from torchvision.transforms.functional import normalize
import numpy as np
from transformers import Pipeline
from transformers.image_utils import load_image
from skimage import io
from PIL import Image

class RMBGPipe(Pipeline):
  def __init__(self,**kwargs):
    Pipeline.__init__(self,**kwargs)
    self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    self.model.to(self.device)
    self.model.eval()

  def _sanitize_parameters(self, **kwargs):
    # parse parameters
    preprocess_kwargs = {}
    postprocess_kwargs = {}
    if "model_input_size" in kwargs : 
      preprocess_kwargs["model_input_size"] = kwargs["model_input_size"]
    if "return_mask" in kwargs: 
      postprocess_kwargs["return_mask"] = kwargs["return_mask"]
    return preprocess_kwargs, {}, postprocess_kwargs

  def preprocess(self,input_image,model_input_size: list=[1024,1024]):
      # preprocess the input 
      orig_im = load_image(input_image)
      orig_im = np.array(orig_im)
      orig_im_size = orig_im.shape[0:2]
      preprocessed_image = self.preprocess_image(orig_im, model_input_size).to(self.device)
      inputs = {
          "preprocessed_image":preprocessed_image,
          "orig_im_size":orig_im_size,
          "input_image" : input_image
      }
      return inputs

  def _forward(self,inputs):
    result = self.model(inputs.pop("preprocessed_image"))
    inputs["result"] = result
    return inputs
  
  def postprocess(self,inputs,return_mask:bool=False ):
    result = inputs.pop("result")
    orig_im_size = inputs.pop("orig_im_size")
    input_image = inputs.pop("input_image")
    result_image = self.postprocess_image(result[0][0], orig_im_size)
    pil_im = Image.fromarray(result_image)
    if return_mask ==True : 
      return pil_im
    no_bg_image = Image.new("RGBA", pil_im.size, (0,0,0,0))
    input_image = load_image(input_image)
    no_bg_image.paste(input_image, mask=pil_im)
    return no_bg_image
    
  # utilities functions
  def preprocess_image(self,im: np.ndarray, model_input_size: list=[1024,1024]) -> torch.Tensor:
    # same as utilities.py with minor modification
    if len(im.shape) < 3:
        im = im[:, :, np.newaxis]
    im_tensor = torch.tensor(im, dtype=torch.float32).permute(2,0,1)
    im_tensor = F.interpolate(torch.unsqueeze(im_tensor,0), size=model_input_size, mode='bilinear')
    image = torch.divide(im_tensor,255.0)
    image = normalize(image,[0.5,0.5,0.5],[1.0,1.0,1.0])
    return image
  
  def postprocess_image(self,result: torch.Tensor, im_size: list)-> np.ndarray:
      result = torch.squeeze(F.interpolate(result, size=im_size, mode='bilinear') ,0)
      ma = torch.max(result)
      mi = torch.min(result)
      result = (result-mi)/(ma-mi)
      im_array = (result*255).permute(1,2,0).cpu().data.numpy().astype(np.uint8)
      im_array = np.squeeze(im_array)
      return im_array
