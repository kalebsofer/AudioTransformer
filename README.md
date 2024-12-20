# AudioTransformer

[Frontend lives here](http://65.109.142.90:8501/)

AudioTransformer is an ongoing personal project based on [Whisper](https://github.com/openai/whisper), and fine-tuned on a [common_voice_11](https://huggingface.co/datasets/mozilla-foundation/common_voice_11_0) for audio transcription tasks. The project is fully containerized, scalable and modularised. It is deployed on a server I rent from Hetzner. 

Whisper transformer architecture:

![Whisper](public/images/whisper.png)


## Project Overview

- **Frontend**: Hosted using a Streamlit server, accessible at [http://65.109.142.90:8501/](http://65.109.142.90:8501/).
- **Backend**: Retrieves the model and performs inference on incoming audio transcription requests.
- **Storage**: MinIO is used to store different versions of the transcription model.
- **RDBS**: PostgreSQL is utilized to log user behavior and interactions.
- **Traffic**: Nginx is configured to handle traffic and SSL termination.

## Deployment

The application is deployed on a remote Hetzner server.

## Container Architecture

The architecture is modular and scalable. Docker containers have a single purpose and are designed to be stateless.

![Container Architecture](public/images/container_architecture.jpg)

## Stack

![Technology Stack](public/images/stack.png)

## Getting Started

To get started with the AudioTransformer project, you can visit the frontend interface at the provided URL and explore the transcription capabilities.

## Contributing

Contributions to the project are welcome. Please feel free to open issues or submit pull requests for any improvements or bug fixes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
