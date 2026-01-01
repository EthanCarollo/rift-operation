from PIL import Image
import coremltools as ct
from coremltools.models.utils import save_spec

model = ct.models.MLModel("MobileNetV2.mlmodel")
spec = model.get_spec()

nn_type = spec.WhichOneof("Type")

old_nn = None
if nn_type == "neuralNetworkClassifier":
    old_nn = spec.neuralNetworkClassifier
elif nn_type == "neuralNetworkRegressor":
    old_nn = spec.neuralNetworkRegressor
else:
    old_nn = spec.neuralNetwork

new_spec = ct.proto.Model_pb2.Model()
new_spec.specificationVersion = spec.specificationVersion
new_nn = new_spec.neuralNetwork

target_layer_name = "MobilenetV2/Logits/Conv2d_1c_1x1/BiasAdd:0"

new_spec.description.input.extend(spec.description.input)

new_output = new_spec.description.output.add()
new_output.name = target_layer_name
new_output.type.multiArrayType.dataType = ct.proto.FeatureTypes_pb2.ArrayFeatureType.FLOAT32
new_output.type.multiArrayType.shape.extend([1, 1, 1000])

for layer in old_nn.layers:
    new_layer = new_nn.layers.add()
    new_layer.CopyFrom(layer)
    if layer.name == target_layer_name:
        break

new_nn.layers[-1].output[0] = target_layer_name

new_spec.description.metadata.CopyFrom(spec.description.metadata)

save_spec(new_spec, "mobilenetv2_truncated.mlmodel")

print("✅ Modèle tronqué enregistré : mobilenetv2_truncated.mlmodel")

truncated = ct.models.MLModel("mobilenetv2_truncated.mlmodel")
print(truncated)

image = Image.open("chat.png")

if image.mode != "RGB":
    image = image.convert("RGB")

image = image.resize((224, 224))

out = truncated.predict({"image": image})
print(out)