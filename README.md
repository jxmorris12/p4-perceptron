# p4-perceptron

This was my final project for CS6114, Software-Defined Networking at Cornell with Nate Foster. I implemented the linear perceptron described in the paper "Binarized Neural Networks" (Hubara et al., 2016) in the networking devices programming language P4.

The main files are:
- `perceptron.py`: creates the initial packet and passes it to the switch over and over until the `pkt.finished` bit is set. Then prints out the answer from the switch, and whether or not it matches the answer given by numpy.
- `perceptron.p4`: implements the perceptron in P4. Most of the hard work is done in the ingress control.

To run this, you need to have Petr4 and mininet installed. Run `make controller` in one window and `make run` in another. In the second window, type `h1 python perceptron.py` to generate random matrices and do the perceptron computation on them. It will print out to let you know if the switch got the same answer as calculated using numpy/linear algebra (it should be the same!). You can run the progam multiple times to see that it works with different randomly-generated values.
