#!/usr/bin/env python3
"""Provide RNN-based models.
"""
import torch.nn as nn


class PureRNN(nn.Module):
    def __init__(self, input_size, output_size, num_layers, hidden_size):
        super(PureRNN, self).__init__()

        self.num_layers = num_layers

        for l in range(num_layers):
            in_size = input_size if l == 0 else hidden_size
            out_size = output_size if l == num_layers - 1 else hidden_size

            self.add_module(
                f'rnn{l}',
                nn.LSTMCell(input_size=in_size, hidden_size=out_size))

    def forward(self, input):
        sequence_length = input.size()[1]
        states = [list() for _ in range(self.num_layers)]
        hidden_t = None

        for t in range(sequence_length):
            for l in range(self.num_layers):
                cell = getattr(self, f'rnn{l}')

                if l == 0:
                    input_t = input[:, t, :].squeeze()
                else:
                    input_t = hidden_t

                if t == 0:
                    hidden_t, cell_t = cell(input_t)
                else:
                    hidden_t, cell_t = cell(input_t, states[l][t-1])

                states[l].append((hidden_t, cell_t))

        return hidden_t


class RNNLinear(nn.Module):
    def __init__(self, input_size, output_size, num_layers, hidden_size):
        super(RNNLinear, self).__init__()

        self.rnn = nn.LSTM(input_size=input_size,
                           hidden_size=hidden_size,
                           num_layers=num_layers,
                           dropout=0.3,
                           batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, input):
        output, _ = self.rnn(input)
        output = self.fc(output[:, -1, :])

        return output
