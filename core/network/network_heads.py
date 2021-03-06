from .network_utils import *
from .network_bodies import *


class VanillaNet(nn.Module, BaseNet):
    def __init__(self, output_dim, body, device):
        super(VanillaNet, self).__init__()
        self.device = device
        self.fc_head = layer_init(nn.Linear(body.feature_dim, output_dim))
        self.body = body
        self.to(device)

    def forward(self, x):
        if not isinstance(x, torch.Tensor):
            x = tensor(x, self.device)
        phi = self.body(x)
        y = self.fc_head(phi)
        return y


class ModulatedNet(nn.Module, BaseNet):
    def __init__(self, output_dim, body, device):
        super(ModulatedNet, self).__init__()
        self.device = device
        self.fc_head = layer_init(nn.Linear(body.feature_dim, output_dim))
        self.body = body
        self.to(device)

    def forward(self, x, phi, proto_embeddings):
        if not isinstance(x, torch.Tensor):
            x = tensor(x, self.device)
        if not isinstance(phi, torch.Tensor):
            phi = tensor(phi, self.device)
        activations = self.body(x)
        # phi = torch.softmax(phi, dim=0).repeat(int(len(activations)/len(phi)))
        # phi = (phi - torch.min(phi)) / (torch.max(phi) - torch.min(phi))
        # if len(phi.size()) > 2:
        #     phi = phi.repeat(int(len(activations)/len(phi)))
        # else:
        #     phi = phi.repeat(1, int(activations.shape[-1]/phi.shape[-1]))

        # For 1 x d phi
        # torch.sum((proto_embeddings - phi)**2, dim=1)

        d = torch.sum((phi.view(len(phi), 1, -1) - proto_embeddings)**2, dim=2)
        d = 1 - (d - torch.min(d)) / (torch.max(d) - torch.min(d))
        d = d.repeat(1, int(activations.shape[-1]/d.shape[-1]))
        y = self.fc_head(activations*d)
        # y = self.fc_head(activations)
        return y


class KennyNet(nn.Module, BaseNet):
    # Using Kenny Young's DQN arch from here: https://github.com/kenjyoung/MinAtar/blob/master/examples/dqn.py
    def __init__(self, in_channels, spatial_length, num_actions, device):
        super(KennyNet, self).__init__()
        self.device = device

        self.conv = nn.Conv2d(in_channels, 16, kernel_size=3, stride=1)

        def size_linear_unit(size, kernel_size=3, stride=1):
            return (size - (kernel_size - 1) - 1) // stride + 1

        num_linear_units = size_linear_unit(10) * size_linear_unit(10) * 16
        self.fc_hidden = nn.Linear(in_features=num_linear_units, out_features=128)
        self.output = nn.Linear(in_features=128, out_features=num_actions)
        self.to(device)

        self.in_channels = in_channels
        self.spatial_length = spatial_length

    def forward(self, x):
        if not isinstance(x, torch.Tensor):
            x = tensor(x, self.device)
        x = F.relu(self.conv(self.shape_image(x)))
        x = F.relu(self.fc_hidden(x.view(x.size(0), -1)))
        return self.output(x)

    def shape_image(self, x):
        return x.reshape(-1, self.spatial_length, self.spatial_length, self.in_channels).permute(0, 3, 1, 2)


class VanillaNet(nn.Module, BaseNet):
    def __init__(self, output_dim, body, device):
        super(VanillaNet, self).__init__()
        self.device = device
        self.fc_head = layer_init(nn.Linear(body.feature_dim, output_dim))
        self.body = body
        self.to(device)

    def forward(self, x):
        if not isinstance(x, torch.Tensor):
            x = tensor(x, self.device)
        phi = self.body(x)
        y = self.fc_head(phi)
        return y


class LinearNet(nn.Module, BaseNet):
    def __init__(self, output_dim, input_dim, device):
        super(LinearNet, self).__init__()
        self.device = device
        self.layer = layer_init(nn.Linear(input_dim, output_dim))
        self.to(device)

    def forward(self, x):
        if not isinstance(x, torch.Tensor):
            x = tensor(x, self.device)
        y = self.layer(x)
        return y