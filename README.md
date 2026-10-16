# Open WebUI CTF - Docker Setup

This project provides a complete Capture The Flag (CTF) environment based on Open WebUI with LLM prompt injection challenges.

## 🚀 Quick Start

### Prerequisites
- Ubuntu 20.04/22.04/24.04 or Debian-based Linux (for automatic setup)
- At least 8GB of RAM available
- 20GB of free disk space (for models and containers)
- (Optional BUT HIGHLY RECOMMENDED) NVIDIA GPU for better performance
- (Optional) AWS Account with Bedrock access for cloud-based LLM models

### Setup Instructions

1. **Clone the repository** (or ensure all files are in place):

    ```bash
   # Your project structure should look like:
   openwebui_ctf/
   ├── .env
   ├── Dockerfile.ctfsetup
   ├── Dockerfile.jupyter
   ├── Dockerfile.ollama
   ├── Dockerfile.openwebui
   ├── README.md
   ├── docker-compose.yml
   ├── docker-compose.override.yml
   ├── setup.sh
   └── openwebui/
       ├── functions/
       │   ├── flag_check_filter.py.template
       │   ├── image_text_filter.py
       │   ├── input_filter.py
       │   ├── output_filter.py.template
       │   └── output_filter_2.py.template
       ├── knowledge/
       │   ├── stargate_secret.txt.template
       │   └── stargate_users.txt
       ├── pipelines/
       │   ├── email_summarizer.py.template
       │   └── prompt_guard.py
       └── tools/
       │   └── calculator.py
       ├── ctf_config.json.template
       ├── run_setup.sh
       └── setup.py

   ```

3. **Install Pre-requisites**:

   To install Docker, GPU drivers, and other prerequisites, run the following:
   ```bash
   ./setup -a -n
   ```
   After setup is completed, you will need to reboot.

4. **Configure the CTF Environment**:

   After installing the pre-requisites and rebooting, run:
   ```bash
   ./setup --ctf
   ```

5. **Wait for services to be ready** (about 2-3 minutes), then check status:

   ```bash
   docker compose logs -f ctf-setup  # Watch setup progress
   ```

7. **Access the CTF**:
   - Open WebUI: http://localhost:4242
   - Admin User: `admin@ctf.local` / `ctf_admin_password`
   - Standard User: `ctf@ctf.local` / `Hellollmworld!`

## 🛌 Amazon Bedrock Integration

This CTF environment includes optional support for Amazon Bedrock, allowing you to use cloud-based LLM models alongside the local Ollama models.

### Bedrock Setup

1. **AWS Credentials**: Before running the CTF setup, ensure you have:
   - AWS Access Key ID
   - AWS Secret Access Key
   - AWS Region with Bedrock access enabled (default: us-east-1)

2. **Configure During Setup**: When running `./setup.sh --ctf`, you'll be prompted to configure AWS Bedrock credentials. The setup will:
   - Ask if you want to configure Bedrock
   - Prompt for your AWS credentials
   - Store them securely in the `.env` file

3. **Manual Configuration**: You can also manually edit the `.env` file:
   ```bash
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   AWS_DEFAULT_REGION=us-east-1
   AWS_REGION=us-east-1
   BEDROCK_PORT=8081
   BEDROCK_API_KEY=bedrock
   ```

4. **Accessing Bedrock in Open WebUI**:
   - Navigate to Settings > Admin Settings > Connections
   - Add a new OpenAI API connection with:
     - **API Base URL**: `http://bedrock-gateway:80/api/v1`
     - **API Key**: `bedrock` (or the value set in BEDROCK_API_KEY)
   - Available models will appear in the model selector

5. **Available Bedrock Models**: The gateway provides access to various Amazon Bedrock models including:
   - Anthropic Claude models (Claude 3 Opus, Sonnet, Haiku)
   - Amazon Titan models
   - AI21 Jurassic models
   - Cohere models
   - Meta Llama models

6. **Embedding Models**: For RAG functionality, you can configure embedding models:
   - Go to Settings > Admin Settings > Documents
   - Set Embedding Model Engine to use Bedrock endpoint
   - Recommended models: `cohere.embed-english-v3` or `cohere.embed-multilingual-v3`

### Bedrock Gateway Details

- **Container**: `bedrock-gateway`
- **Port**: 8081 (configurable via BEDROCK_PORT in .env)
- **API Endpoint**: `http://localhost:8081/api/v1`
- **Health Check**: `http://localhost:8081/health`

The Bedrock Gateway provides an OpenAI-compatible API, making it seamless to use with Open WebUI.

### What the `bedrock` branch captures

This branch is the reproducible Bedrock build of the CTF. Clone it, put your AWS keys in `.env`, run `docker compose up`, and the whole stack (gateway included) comes up on Bedrock with no manual out-of-band steps.

- **AWS prerequisites (do this first).** Valid keys alone are not enough. In the Bedrock console, enable model access for Llama 3.3 70B, Llama 4 Scout, and Llama 3.1 8B in your region, and use keys whose IAM allows `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream` on both the foundation-model ARNs and the `us.`-prefixed inference-profile ARNs. Set `AWS_REGION`/`AWS_DEFAULT_REGION` to that region (the workshop ran in `us-west-2`). The model IDs committed here are the exact inference-profile IDs that ran live, so they invoke as-is once access is granted. If you change `BEDROCK_API_KEY` in `.env`, keep it equal to the gateway connection key in `openwebui/ctf_config.json.template`.
- **Vendored, patched gateway.** `bedrock-gateway/` is a copy of [aws-samples/bedrock-access-gateway](https://github.com/aws-samples/bedrock-access-gateway) with a local patch to `api/models/bedrock.py::_reframe_multi_payloard` that appends a trailing `user` turn so Challenge 7 (code interpreter) works over Bedrock's Converse API. `Dockerfile.bedrock` builds from this vendored source. Do NOT swap it for a fresh upstream `git clone` or the patch is lost.
- **Challenge model routing (matches the live workshop).** Text challenges (1-7, 9, 10, flag checker) route to `us.meta.llama3-3-70b-instruct-v1:0`; Challenge 11 (multi-modal) routes to `us.meta.llama4-scout-17b-instruct-v1:0`; Challenge 8 (agent) routes to `us.meta.llama3-1-8b-instruct-v1:0` with `function_calling: native`. These IDs are `us.`-prefixed inference profiles (required for on-demand Bedrock in `us-*` regions).
- **Challenge 8 caveat.** Native function-calling plus the "honor tool requests" system-prompt line are captured exactly as run live, but Ch8 was never confirmed end-to-end solvable: the safety-tuned 8B model, combined with the calculator tool's own "dangerously insecure / eval()" description, makes it refuse to call the tool. To make it reliably solvable, soften that tool description in `openwebui/tools/` and/or move Ch8 to a stronger model.
- **Challenge 11 image filter.** `openwebui/functions/image_text_filter.py` carries the v0.5 fix (detects inline `image_url` content; never `.strip()`s list content).
- **Smoke test.** After `docker compose up -d`, run `./scripts/smoke-bedrock.sh` to confirm the gateway is healthy and serving Bedrock models and that Open WebUI is up.

8. **Modifying the flags and credentials**

   The `.env` file contains all of the flags, credentials, and other settings.

   Note that files containing flag placeholders (e.g. ${CTF_CHALLENEGE_FLAG_1) end in .template. These files will be dynamically updated during the setup process. The flag placeholders are replaced with the corresponding flags in the .env file.

10. **Modifying the system prompts**

    The system prompts for each challenge can be found in `openwebui/ctf_config.json.template`.
   
    Be careful not to modify the placeholder for the flags.

11. **Adding/modifying challenges**

    The challenges are also found in `openwebui/ctf_config.json.template`.


## 🎯 CTF Challenges

The CTF includes 11 challenges:

1. **Challenge 1: Hello prompt injection!** - Basic prompt injection
2. **Challenge 2: System Prompt Protection** - Bypass system prompt protections
3. **Challenge 3: Input Filtering** - Defeat input filters
4. **Challenge 4: Output Filtering** - Bypass output filters
5. **Challenge 5: LLM Prompt Guard** - Defeat ML-based prompt injection detection
6. **Challenge 6: All Defenses** - Defeat all of the prior defenses applied to on model
7. **Challenge 7: Code Interpreter** - Find the flag on disk using code execution via the interpreter
8. **Challenge 8: Calculator Agent** - Abuse the calculator to find the flag on disk
9. **Challenge 9: RAG** - Find the flag in the documents
10. **Challenge 10: Email Summarizer** - Trick the email summarizer into sending an email to a target, which will give you the flag
10. **Challenge 11: Multi-Modal** - Use a method other than text to retrieve the flag

## 🚩 Checking Flags

The CTF has a model that users can use to check if a flag is correct.

The model is **Flag Checker** and can be selected just like any of the challenges can be.

Send a potential flag as a prompt and it will tell you if it was correct or not.

This model is templated, so it is dynamically updated when flags are changed in the .env file.

## 🛠️ Service Details

| Service | Port | Description |
|---------|------|-------------|
| Open WebUI | 4242 | Main CTF interface |
| Bedrock Gateway | 8081 | AWS Bedrock API proxy (OpenAI-compatible) |
| Ollama | 11434 | LLM model server (local) |
| Pipelines | 9099 | Custom processing pipelines |
| Jupyter | 8888 | Code execution environment |

## 📝 Managing the CTF

### View logs:
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f open-webui
```

### Restart services:
```bash
docker compose restart
```

### Reset the CTF:
```bash
docker compose down -v  # Remove all data
docker compose up -d    # Start fresh
```

### Stop everything:
```bash
docker compose down
```

## 🔧 Troubleshooting

### Error Message when Entering a Prompt
Sometimes you might receive an error message (typically about JSON parsing or unexpected characters) when entering a prompt to one of the challenges. Logging out and logging back in seems to clear the issue in most cases. We will investigate this error further.

### Bedrock Gateway Issues

**Container fails to start:**
```bash
# Check logs
docker compose logs bedrock-gateway

# Common issues:
# - Invalid AWS credentials
# - No Bedrock access in the specified region
# - Network connectivity issues
```

**Models not appearing in Open WebUI:**
- Verify the API connection settings in Open WebUI
- Ensure the API Base URL is `http://bedrock-gateway:80/api/v1` (internal Docker network)
- Check that the API key matches the value in `.env` (default: `bedrock`)
- Verify AWS credentials have proper Bedrock permissions

**Authentication errors:**
- Check that AWS credentials in `.env` are correct
- Ensure the IAM user/role has `bedrock:InvokeModel` permissions
- Verify Bedrock is available in the configured region

**Health check failing:**
```bash
# Test the gateway directly
curl http://localhost:8081/health
```

### No GPU / CPU-Only Mode
The CTF can run without a GPU but it will be very, very slow.

### GPU Support Issues

### Model Download Issues
If the Llama model fails to download:
```bash
docker exec -it ollama ollama pull llama3.1:8b
```

### Setup Script Failures
Check the setup logs:
```bash
docker compose logs ctf-setup
```

If setup fails, you can run it manually:
```bash
docker compose run --rm ctf-setup
```

### Port Conflicts
If ports are already in use, modify the `.env` file to change port mappings.

## 🏁 CTF Flag Locations

Without spoiling the challenges, here's where flags are stored:
- Challenges 1-6: In the system prompts of each model
- Challenge 7: In the Jupyter container filesystem
- Challenge 8: In the open-webui container filesystem
- Challenge 9: In one of the RAG documents
- Challenge 10: The flag will be returned if the email summarizer sends a specific email to a target recipient
- Challenge 11: In the system prompt of the model

## 👥 Creating Additional Users
By default, users can sign themselves up.

To add more CTF participants as part of the automation process, modify `openwebui/ctf_config.json.template` and add users to the `users` array, then re-run the setup:
```bash
docker compose run --rm ctf-setup
```

## 📚 Resources

- [Open WebUI Documentation](https://github.com/open-webui/open-webui)
- [Ollama Documentation](https://ollama.ai/)
- [LLM Security Resources](https://github.com/llm-security)

Good luck with the CTF! 🚩
