# GAN

This is a small test of using a GAN to generate numbers that look as someone's handwriting when not trained on all numbers. For example we saw someone write the number 273 and we now predict how 481 looks like. 

Main inspiration for doing this is a paper I read recently on Star GAN v2. In this paper they try to recognize diferent latent spaces on the data used and making predictions. For example they are able to use image of different animals like dogs or tigers and making them look like a cat. 

The main focus of this notebook is to try out a simple implementation of this GAN network and see how well it can perform. The way in which it encodes style on its own is the main reason I want to implement this project.

Currently I am thinking of other projects where I am thinking how to implement a system that classifies the style of different inputs and is able to work differently on the input based on this new variable. 

*For anyone interested it will be a project in the Hearthstone folder of this repository. 

For a small tutorial on how to write a GAN I looked at: https://machinelearningmastery.com/how-to-develop-a-generative-adversarial-network-for-an-mnist-handwritten-digits-from-scratch-in-keras/

Link to Star GAN v2: https://app.wandb.ai/stacey/stargan/reports/Cute-Animals-and-Post-Modern-Style-Transfer%3A-StarGAN-v2-for-Multi-Domain-Image-Synthesis---VmlldzoxNzcwODQ
