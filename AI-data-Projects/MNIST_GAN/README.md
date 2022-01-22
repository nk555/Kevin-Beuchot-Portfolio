# MNIST learns your handwriting

This is a small project on using a GAN to generate numbers that look as someone else's handwriting when not trained on all numbers written by this person. For example say we had someone write the number 273 and we now want to write 481 in their own handwriting.

The main inspiration for this project is a paper I read recently called STAR GAN v2. In this paper they try to recognize diferent styles and features in images and transfer those into a different image. For example they are able to use image of different animals like dogs or tigers and making them look like a cat. Furthermore at the time of writing this it is currently a state-of-the-art method for this style translation tasks.

Some of the results can be seen at the end of this notebook. Unfortunately it seems not that many features were captured and mostly it was only the thickness of the numbers that was preserved. A reason this happens might be that the size of the images is small being 28x28. However, some ways to allow for more variation might be by exteding the number of layers being used, by having higher dimensional spaces for the latent and style spaces, or by giving a higher weight to the style diversification loss (look at section loss functions to see more about this).

The main purpose of this notebook is to make a small showcase of the architecture used in a simple design so that the ideas are simple to follow. This notebook will also contain some explanations and comments on the architecture of the neural network so that it might be easier to follow.

Note: another small thing I did in this project is to 'translate' STAR GAN code from pytorch to tensorflow. Redoing all of the work was useful to understand everything done on their code and having an option in tensorflow might be useful for some people.

For a small tutorial on how to write a simple GAN architecture: https://machinelearningmastery.com/how-to-develop-a-generative-adversarial-network-for-an-mnist-handwritten-digits-from-scratch-in-keras/

Link to STAR GAN v2: https://app.wandb.ai/stacey/stargan/reports/Cute-Animals-and-Post-Modern-Style-Transfer%3A-StarGAN-v2-for-Multi-Domain-Image-Synthesis---VmlldzoxNzcwODQ

Further Reading on style domain techniques for image generation:

Link to STAR GAN paper: https://arxiv.org/pdf/1912.01865.pdf

Link to Multimodal Unsupervised Image-to-Image Translation: https://arxiv.org/pdf/1804.04732.pdf

Link to Improving Style-Content Disentanglement Paper: https://arxiv.org/pdf/2007.04964.pdf