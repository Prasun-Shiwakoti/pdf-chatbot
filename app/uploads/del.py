from huggingface_hub import InferenceClient
import json
import json_repair
from json_repair import repair_json
import re
import requests


# Define the API Key and ImgBB upload endpoint
IMGBB_API_KEY = '22b2b02f510a75b10a767f5c2bc62eea'  # Replace with your API key
IMGBB_UPLOAD_URL = 'https://api.imgbb.com/1/upload'
HUGGINGFACE_API_KEY = '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'

client = InferenceClient(api_key=HUGGINGFACE_API_KEY)

def remove_special_sequences(input_string):
    # Replace special escape sequences with a single space
    input_string = re.sub(r'\s+', ' ', input_string).strip()
    special_sequences = [r'\n', r'\t', r'\r', r'\v', r'\a', '\n', '\t', '\r', '\v', '\a']
    for sequence in special_sequences:
        input_string = input_string.replace(sequence, '')
    return input_string

def parse_json_garbage(s):
    cleaned_s = remove_special_sequences(s)
    parsed_s = cleaned_s[next(idx for idx, c in enumerate(s) if c in "{["):]
    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        print("\n\n\nThis was the string:", parsed_s)
        print("\n\n\nThis was the error:", e)
        repaird_s = repair_json(parsed_s)
        print("\n\n\nThis was the repaired string:", json.loads(repaird_s))
        try:
            return json_repair.loads(repaird_s)
        except:
            raise Exception

def callAPI(messages, model="meta-llama/Llama-3.2-3B-Instruct", max_tokens=2048, temperature=0.1):
    completion = client.chat.completions.create(
        model=model, 
        messages=messages, 
        max_tokens=max_tokens,
        temperature=temperature,
        # response_format="json",
    )
    return completion


def generate_notes(context):
    notes_messages =  [
        {
            "role": "system",
            "content": """You are a student. You are creating notes for yourself. You need to generate notes based on the content provided in the messages. 
                Requirements:
                1. The notes should be concise and relevant to the content provided in the messages.Notes should be easy to understand and should contain only the key points.
                2. Use markdown and LaTeX if needed for better readability.
                3. Always respond in json format: {"notes":"notes"}.
                4. Output only the JSON. Do not include any additional explanation, headers, or text.
                5. Double-check the correctness of your response format and notes before submitting.
        """
        },

        {
            "role": "user",
            "content": f"""Generate notes based on context given below:
                Context: {context}
            """
        }
    ]
    
    notes = callAPI(notes_messages)
    try:
        notes_json = parse_json_garbage(notes.choices[0].message.content)
    except:

        notes_messages[1]['content'] += "\nRequirement: Strictly follow the JSON format"
        notes = callAPI(notes_messages)
        notes_json = parse_json_garbage(notes.choices[0].message.content)
    return notes_json


def generate_quiz(context):
    quiz_messages = [
        {
            "role": "system",
            "content": """You are a teacher. You are creating a quiz for your students. You need to generate questions and answers for the quiz. 
        Requirements:
        1. The questions should be multiple choice questions. The answers should be one of the choices in the multiple choice questions. Include all type of questions like true/false, multiple choice, etc.
        2. The questions should be relevant to the content provided in the messages. Generate unique quesitons and answers ervery time.
        3. Always respond in json format: {"questions": [{"question":"question", "choices":["choice1", "choice2", "choice3", "choice4"], "answer":"answer"},...]}
        4. Output only the JSON. Do not include any additional explanation, headers, or text.
        5. Double-check the correctness of your response format, questions and answers before submitting.
        """
        },

        {
            "role": "user",
            "content": f"""Generate multiple choice question based on context given below:
                Context: {context}
            """
        }
    ]

    questions = callAPI(quiz_messages)
    for _ in range(3):
        try:
            quiz_json = parse_json_garbage(questions.choices[0].message.content)
            break
        except:
            quiz_messages[1]['content'] += "\nRequirement: Strictly follow the JSON format"
            quiz_messages = callAPI(quiz_messages)
            quiz_json = parse_json_garbage(quiz_messages.choices[0].message.content)
    return quiz_json


def generate_flashcard(context):
    flashcards_messages = [
        {
            "role": "system",
            "content": """You are creating flashcards based on the provided context. 
            Requirements:
            1. The flashcards should contian key points from the content provided in the messages.
            2. The points should be clear and concise.
            3. Always respond in JSON format:
                {"flashcards":["information1", "information2", "information3", ...]}
            4. Output only the JSON. Do not include any additional explanation, headers, or text.
            5. Double-check and validate the correctness of json format before submitting.
            """
        },
        {
            "role": "user",
            "content": f"""Generate flashcards based on the context provided below: 
            Context: {context}"""
        }

    ]

    flashcards = callAPI(flashcards_messages)
    for _ in range(3):
        try:
            flashcards_json = parse_json_garbage(flashcards.choices[0].message.content)
            break
        except:
            flashcards_messages[1]['content'] += "\nRequirement: Strictly follow the JSON format"
            flashcards = callAPI(flashcards_messages)
    
    return flashcards_json

def generate_chat(context, prompt):
    messages = [
        {
            "role": "system",
            "content": """You are a helpful AI assistant. Be conversational and friendly. Reply based on the context provided as long as it contains required information else use your own knowledge to generate a response."""
        },
        
        {
            "role": "user",
            "content": f"""Context: {context}
                User Prompt: {prompt}"""
        }
    ]
    completion = callAPI(messages)
    response = completion.choices[0].message.content
    return response

# Function to upload image to ImgBB
def upload_to_imgbb(image_path):
    with open(image_path, 'rb') as image_file:
        response = requests.post(
            IMGBB_UPLOAD_URL,
            params={'key': IMGBB_API_KEY},
            files={'image': image_file}
        )
        response_data = response.json()
        if response.status_code == 200 and response_data['success']:
            return response_data['data']['url']
        return None    

def extract_text_from_image(url):
    print("Extracting text from image...", url)
    img_url = url 
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """Extract the text from the image. 
                        Requirements: 
                        1. Use markdown or LaTeX wherever needed.
                        2. Output only the text. Do not include any additional explanation, headers, or text.
                        3. Double check the correctness of your response before submitting.
                    """
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": img_url
                    }
                }
            ]
        }
    ]
    stream = client.chat.completions.create(
        model="meta-llama/Llama-3.2-11B-Vision-Instruct",
        messages=messages,
        max_tokens=2000,
        stream=True
    )
    extracted_text = ""
    for chunk in stream:
        extracted_text += chunk.choices[0].delta.content

    return extracted_text
    extracted_text = remove_special_sequences(extracted_text)
    parsed_text = parse_json_garbage(extracted_text)
    return parsed_text

def summarize_text(text):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

    payload = {
        "inputs": text,
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()[0].get("summary_text", "No summary text found")
            

print(summarize_text("{\\[  \"text\": \"Attention Is All You Need\n\nAbstract\n\nThe dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallellizable and requiring significantly  less time to train. \n\nOur model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU. On the WMT 2014 English-to-French translation task,  our model establishes a new single-model state-of-the-art BLEU score of 41.0 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature.\n\n1 Introduction\n\nRecurrent neural networks, long short-term memory \\[12] and gated recurrent [7] neural networks in particular, have been firmly established as state of the art approaches in sequence modeling and  transduction problems such as language modeling and machine translation [29, 2, 5, 31, 21, 13].\n\nNumerous efforts have since continued to push the boundaries of recurrent language models and encoder-decoder architectures [31, 21, 13].\n\n\\* Equal contribution. Listing order is random. Jakob proposed replacing RNNs with self-attention and started the effort to evaluate this idea. Ashish, with Illia, designed and implemented the first Transformer models and  has been crucially involved in every aspect of this work. Noam proposed scaled dot-product attention, multi-head attention and the parameter-free position representation and became the other person involved in nearly every detail. Niki designed, implemented, tuned and evaluated countless model variants in our original codebase and  tensor2tensor. Llion also experimented with novel model variants, was responsible for our initial codebase, and  efficient inference and visualizations. Lukasz and Aidan spent countless long days designing various parts of and  implementing tensor2tensor, replacing our earlier codebase, greatly improving results and massively accelerating  our research.\n\n\\* Work performed while at Google Brain.\n\n\\* Work performed while at Google Research.\n\n31st Conference on Neural  Information Processing Systems (NIPS 2017), Long Beach, CA, USA.\"   \\]}{\"text\":\"Recurrent models typically factor computation along the symbol positions of the input and output sequences. Aligning the positions to steps in computation time, they generate a sequence of hidden states $h_t$, as a function of the previous hidden state $h_{t-1}$ and the input for position $t$. This inherently sequential nature precludes parallelization within training examples, which becomes critical at longer sequence lengths, as memory constraints limit batching across examples. Recent work has achieved significant improvements in computational efficiency through factorization tricks [18] and conditional computation [26], while also improving model performance in case of the latter. The fundamental constraint of sequential computation, however, remains.\n\nAttention mechanisms have become an integral part of compelling sequence modeling and transduction models in various tasks, allowing modeling of dependencies without regard to their distance in the input or output sequences [2] [16]. In all but a few cases [22], however, such attention mechanisms are used in conjunction with a recurrent network.\n\nIn this work we propose the Transformer, a model architecture eschewing recurrence and instead relying entirely on an attention mechanism to draw global dependencies between input and output. The Transformer allows for significantly more parallelization and can reach a new state of the art in translation quality after being trained for as little as twelve hours on eight P100 GPUs.\n\nThe goal of reducing sequential computation also forms the foundation of the Extended Neural GPU [20], ByteNet [15] and ConvS2S [8], all of which use convolutional neural networks as basic building block, computing hidden representations in parallel for all input and output positions. In these models, the number of operations required to relate signals from two arbitrary input or output positions grows in the distance between positions, nearly for ConvS2S and logarithmically for ByteNet. This makes it more difficult to learn dependencies between distant positions [11]. In the Transformer this is reduced to a constant number of operations, albeit at the cost of reduced effective resolution due to averaging attention-weighted positions, an effect we counteract with Multi-Head Attention as described in section [3.2].\n\nSelf-attention, sometimes called intra-attention is an attention mechanism relating different positions of a single sequence in order to compute a representation of the sequence. Self-attention has been used successfully in a variety of tasks including reading comprehension, abstractive summarization, textual entailment and learning task-independent sentence representations [4] [22] [23] [19].\n\nEnd-to-end memory networks are based on a recurrent attention mechanism instead of sequence-aligned recurrence and have been shown to perform well on simple-language question answering and language modeling tasks [28].\n\nTo the best of our knowledge, however, the Transformer is the first transduction model relying entirely on self-attention to compute representations of its input and output without using sequence-aligned RNNs or convolution. In the following sections, we will describe the Transformer, motivate self-attention and discuss its advantages over models such as [14] [15] and [8].\"}{\"text\":\"Figure 1: The Transformer - model architecture.\"}{\"text\": \"Figure 2: (left) Scaled Dot-Product Attention. (right) Multi-Head Attention consists of several attention layers running in parallel.\n\nquery with all keys, divide each by √dk, and apply a softmax function to obtain the weights on the values.\n\nIn practice, we compute the attention function on a set of queries simultaneously, packed together into a matrix Q. The keys and values are also packed together into matrices K and V. We compute the matrix of outputs as:\n\nAttention(Q, K, V) = softmax( QK^T / √dk ) V\n\nThe two most commonly used attention functions are additive attention []1, and dot-product (multi-plicative) attention. Dot-product attention is identical to our algorithm, except for the scaling factor of 1/√dk. Additive attention computes the compatibility function using a feed-forward network with a single hidden layer. While the two are similar in theoretical complexity, dot-product attention is much faster and more space-efficient in practice, since it can be implemented using highly optimized matrix multiplication code.\n\nWhile for small values of dk the two mechanisms perform similarly, additive attention outperforms dot product attention without scaling for larger values of dk []3. We suspect that for large values of dk, the dot products grow large in magnitude, pushing the softmax function into regions where it has extremely small gradients []4. To counteract this effect, we scale the dot products by 1/√dk.\n\nInstead of performing a single attention function with dm dimensional keys, values and queries, we found it beneficial to linearly project the queries, keys and values h times with different, learned linear projections to dm, dk and dm, respectively. On each of these projected versions of queries, keys and values we then perform the attention function in parallel, yielding dm dimensional output values. These are concatenated and once again projected, resulting in the final values, as depicted in Figure []2.\n\nMulti-head attention allows the model to jointly attend to information from different representation subspaces at different positions. With a single attention head, averaging inhibits this.\n\n[] To illustrate why the dot products get large, assume that the components of q and k are independent random variables with mean 0 and variance 1. Then their dot product, q · k = ∑dki=1 qi ki, has mean 0 and variance dk. This is because the mean value of the product of two independent random variables with mean 0 is 0, and the variance of the product of two independent random variables with variance 1 is the product of their variances. Therefore, the variance of the dot product is dk.\"}{\"text\": \"MultiHead$(Q,K,V) = Concat(head_1,..., head_n)W^O\n\nwhere head_i = Attention(QW^Q, KW^K, VW^V)\n\nWhere the projections are parameter matrices W^Q  ∈ ℝ^{d_model × d_k}, W^R  ∈ ℝ^{d_model × d_k}, W^V  ∈ ℝ^{d_model × d_v} and W^O  ∈ ℝ^{h × d_model}.\n\nIn this work we employ h = 8 parallel attention layers, or heads. For each of these we use d_k = d_v = d_model/h = 64. Due to the reduced dimension of each head, the total computational cost is similar to that of single-head attention with full dimensionality.\n\n3.2.3 Applications of Attention in our Model\n\nThe Transformer uses multi-head attention in three different ways:\n\nIn \\\"encoder-decoder attention\\\" layers, the queries come from the previous decoder layer, and the memory keys and values come from the output of the encoder. This allows every position in the decoder to attend over all positions in the input sequence. This mimics the typical encoder-decoder attention mechanisms in sequence-to-sequence models such as \n\nThe encoder contains self-attention layers. In a self-attention layer all of the keys, values and queries come from the same place, in this case, the output of the previous layer in the encoder. Each position in the encoder can attend to all positions in the previous layer of the encoder.\n\nSimilarly, self-attention layers in the decoder allow each position in the decoder to attend to all positions in the decoder up to and including that position. We need to prevent leftward information flow in the decoder to preserve the auto-regressive property. We implement this inside of scaled dot-product attention by masking out (setting to  ∞) all values in the input of the softmax which correspond to illegal connections. See Figure\n\n3.3 Position-wise Feed-Forward Networks\n\nIn addition to attention sub-layers, each of the layers in our encoder and decoder contains a fully connected feed-forward network, which is applied to each position separately and identically. This consists of two linear transformations with a ReLU activation in between.\n\nFFN(x) = max(0, xW_1 + b_1)W_2 + b_2\n\nWhile the linear transformations are the same across different positions, they use different parameters from layer to layer. Another way of describing this is as two convolutions with kernel size 1. The dimensionality of input and output is d_model = 512, and the inner-layer has dimensionality d_ff = 2048.\n\n3.4 Embeddings and Softmax\n\nSimilarly to other sequence transduction models, we use learned embeddings to convert the input tokens and output tokens to vectors of dimension d_model_. We also use the usual learned linear transformation and softmax function to convert the decoder output to predicted next-token probabilities. In our model, we share the same weight matrix between the two embedding layers and the pre-softmax linear transformation, similar to\n\nIn the embedding layers, we multiply those weights by √d_model\n\n3.5 Positional Encoding\n\nSince our model contains no recurrence and no convolution, in order for the model to make use of the order of the sequence, we must inject some information about the relative or absolute position of the tokens in the sequence. To this end, we add \\\"position encodings\\\" to the input embeddings at the end,\"}{\"text\":\"\\\\section*{Why Self-Attention}In this section we compare various aspects of self-attention layers to the recurrent and convolutional layers commonly used for mapping one variable-length sequence of symbol representations $(x_1,\\ldots,x_n)$ to another sequence of equal length $(z_1,\\ldots,z_n)$, with $x_i,s \\in\\\\mathbb{R}^d$, such as a hidden layer in a typical sequence transduction encoder or decoder. Motivating our use of self-attention we consider three desiderata.\n\n\\\textbf{One is the total computational complexity per layer.} Another is the amount of computation that can be parallelized, as measured by the minimum number of sequential operations required.\n\nThe third is the path length between long-range dependencies in the network. Learning long-range dependencies is a key challenge in many sequence transduction tasks. One key factor affecting the ability to learn such dependencies is the length of the paths forward and backward signals have to traverse in the network. The shorter these paths between any combination of positions in the input and output sequences, the easier it is to learn long-range dependencies \\\textit{[11]}.\n\nHence we also compare the maximum path length between any two input and output positions in networks composed of the different layer types.\n\nAs noted in Table  \\\textit{[1]}, a self-attention layer connects all positions with a constant number of sequentially executed operations, whereas a recurrent layer requires $O(n)$ sequential operations. In terms of computational complexity, self-attention layers are faster than recurrent layers when the sequence length $n$ is smaller than the representation dimensionality $d$, which is most often the case with sentence representations used by state-of-the-art models in machine translations, such as word-piece \\\textit{[31]} and byte-pair \\\textit{[25]} representations.\n\nTo improve computational performance for tasks involving very long sequences, self-attention could be restricted to considering only a neighborhood of size $r$ in...\n\nWe also experimented with using learned positional embeddings \\\textit{[8]} instead, found that the two versions produced nearly identical results (see Table \\\textit{[2]} row (E)). We chose the sinusoidal version because it may allow the model to extrapolate to sequence lengths longer than the ones encountered during training.\n\nIn this section we compare various aspects of self-attention layers to the recurrent and convolutional layers commonly used for mapping one variable-length sequence of symbol representations $(x_1,\\ldots,x_n)$ to another sequence of equal length $(z_1,\\ldots,z_n)$, with $x_i,s \\in\\\\mathbb{R}^d$, such as a hidden layer in a typical sequence transduction encoder or decoder. Motivating our use of self-attention we consider three desiderata.\n\n\\\textbf{One is the total computational complexity per layer}. Another is the amount of computation that can be parallelized, as measured by the minimum number of sequential operations required.\n\nThe third is the path length between long-range dependencies in the network. Learning long-range dependencies is a key challenge in many sequence transduction tasks. One key factor affecting the ability to learn such dependencies is the length of the paths forward and backward signals have to traverse in the network. The shorter these paths between any combination of positions in the input and output sequences, the easier it is to learn long-range dependencies \\\textit{[11]}.\n\nHence we also compare the maximum path length between any two input and output positions in networks composed of the different layer types.\n\nAs noted in Table  \\\textit{[1]}, a self-attention layer connects all positions with a constant number of sequentially executed operations, whereas a recurrent layer requires $O(n)$ sequential operations. In terms of computational complexity, self-attention layers are faster than recurrent layers when the sequence length $n$ is smaller than the representation dimensionality $d$, which is most often the case with sentence representations used by state-of-the-art models in machine translations, such as word-piece \\\textit{[31]} and byte-pair \\\textit{[25]} representations.\n\nTo improve computational performance for tasks involving very long sequences, self-attention could be restricted to considering only a neighborhood of size $r$ in a self-attention layer connects all positions with a constant number of sequentially executed operations, whereas a recurrent layer requires $O(n)$ sequential operations. In terms of computational complexity, self-attention layers are faster than recurrent layers when the sequence length $n$ is smaller than the representation dimensionality $d$, which is most often the case with sentence representations used by state-of-the-art models in machine translations, such as word-piece \\\textit{[31]} and byte-pair \\\textit{[25]} representations.\"}\"}{\"text\": \"the input sequence centered around the respective output position. This would increase the maximum path length to $O(n/r)$. We plan to investigate this approach further in future work.\\\nA single convolutional layer with kernel width $k\u003Cn$ does not connect all pairs of input and output positions. Doing so requires a stack of $O(n/k)$ convolutional layers over contiguous kernels, or $O(\\log_k(n))$ in the case of dilated convolutions $[15]$, increasing the length of the longest paths between any two positions in the network. Convolutional layers are generally more expensive than recurrent layers, by a factor of $k$. Separable convolutions $[6]$, however, decrease the complexity considerably, to $O(k\\cdot n\\cdot d+n\\cdot d^2)$. Even with $k=n$, however, the complexity of a separable convolution is equal to the combination of a self-attention layer and a point-wise feed-forward layer, the approach we take in our model.\\\nAs side benefit, self-attention could yield more interpretable models. We inspect attention distributions from our models and present and discuss examples in the appendix. Not only do individual attention heads clearly learn to perform different tasks, many appear to exhibit behavior related to the syntactic and semantic structure of the sentences.\\\n**Training**\\\nThis section describes the training regime for our models.\\\n**5.1 Training Data and Batching**\\\nWe trained on the standard WMT 2014 English-German dataset consisting of about 4.5 million sentence pairs. Sentences were encoded using byte-pair encoding $[3]$, which has a shared source-target vocabulary of about 37000 tokens. For English-French, we used the significantly larger WMT 2014 English-French dataset consisting of 36M sentences and split tokens into a 32000 word-piece vocabulary $[31]$. Sentence pairs were batched together by approximate sequence length. Each training batch contained a set of sentence pairs containing approximately 25000 source tokens and 25000 target tokens.\\\n**5.2 Hardware and Schedule**\\\nWe trained our models on one machine with 8 NVIDIA P100 GPUs. For our base models using the hyperparameters described throughout the paper, each training step took about 0.4 seconds. We trained the base models for a total of 100,000 steps or 12 hours. For our big models, (described on the bottom line of table$[3]$, step time was 1.0 seconds. The big models were trained for 300,000 steps (3.5 days).\\\n**5.3 Optimizer**\\\nWe used the Adam optimizer $[17]$ with $\\\beta_1 = 0.9$, $\\\beta_2 = 0.98$ and $\\\\epsilon = 10^{-9}$. We varied the learning rate over the course of training, according to the formula:$$\\\n\\\rate = d^{-0.5\\\\cdot\\\\min(M \\\\cdot\\\\step_{num}^{-0.5},\\\\step_{num}\\\\cdot\\\\warmup_{steps}^{-1.5})}\\\n$$This corresponds to increasing the learning rate linearly for the first $warmup\\_steps$ training steps, and decreasing it thereafter proportionally to the inverse square root of the step number. We used $warmup\\_steps = 4000$.\\\n**5.4 Regularization**\\\nWe employ three types of regularization during training:$$\\\n\\\textbf{Residual Dropout}$$\\\nWe apply dropout $[27]$ to the output of each sub-layer, before it is added to the sub-layer input and normalized. In addition, we apply dropout to the sums of the embeddings and the positional encodings in both the encoder and decoder stacks. For the base model, we use a rate of $P_{drop}=0.1$.\"}{\"text\":\"Table 1: Comparison of different models\u000bspace{.5em}\n\n| Model | Training Objectives | Accuracy | BLEU-4 Score | Test Time (s) | Training Time (s) | Parameters |\n| --- | --- | --- | --- | --- | --- | --- |\n| Vanilla Transformer | Maximum Likelihood Estimation | 49.52 | 34.14 | 2.77 | 507.31 | 67.5M |\n| Vanilla Transformer + Tied Embedding | Maximum Likelihood Estimation | 49.23 | 33.53 | 3.21 | 392.11 | 67.5M |\n| Shape Normalized Transformer | Shape Classification | 50.11 | 35.04 | 2.92 | 548.17 | 67.5M |\n| Size Normalized Transformer | Size Classification | 50.22 | 35.12 | 2.86 | 537.89 | 67.5M |\n| Shape and Size Normalized Transformer | Shape and Size Classification | 50.30 | 35.41 | 2.88 | 554.98 | 67.5M |\n\n\u000bspace{.5em}\n\nTable 2: Comparison of different models with precomputed shapes\u000bspace{.5em}\n\n| Model | Training Objectives | Accuracy | BLEU-4 Score | Test Time (s) | Training Time (s) | Parameters |\n| --- | --- | ---|---| --- | --- | --- |\n| Precomputed Shape Normalized Transformer | Shape Classification | 51.02 | 36.34 | 2.89 | 521.41 | 67.5M |\n| Precomputed Shape and Size Normalized Transformer | Shape and Size Classification | 51.18 | 36.64 | 2.93 | 547.31 | 67.5M |\n\n\u000bspace{.5em}\n\nOur approach consists of three stages: pre-computation, model modification, and fine-tuning.\\section{Pre-computation}\nIn the pre-computation phase, we not only compute the pre-computed shape and size embedding directly, but also construct six sets of shape and size features for each shape and size (e.g. vectors for 3D shapes).\\section{Model modification}\nIn the model modification phase, we set parameters of shape and size embeddings to values that are obtained in the pre-computation phase.\\section{Fine-tuning}\nIn this phase, we fine-tune the shape and size embeddings for all models and compute the accuracy on the test data.\u000bspace{.5em}\n\nA major experiment consists of eight models being trained.\\section{Experimental setup}\nBased on the strategy outlined in the previous section, we set programmable attributes to evaluate all the different setups by varying model architectures and varied strategies for training.\"}{\"text\": \"# Varitions on the Transformer architecture. Unlisted values are identical to those of the base model. All metrics are on the English-to-German translation development set, newstest2013. Listed perplexities are per-wordpiece, according to our byte-pair encoding, and should not be compared to per-word perplexities.\n\n|  | $d\\_model$ | $d\\_ff$ | $h$ | $d\\_k$ | $d\\_v$ | $\\epsilon\\_ls$ | train steps | PPL(dev) | BLEU(dev) | params $\times10^6$ |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n| base | 6 | 512 | 8 | 64 | 0.1 | 100K | 4.92 | 25.8 | 65 |  |\n|  |  |  | 1 | 512 |  |  | 5.29 | 24.9 |  |  |\n|  |  |  | 4 | 128 |  |  | 5.00 | 25.5 |  |  |\n|  |  |  | 16 | 32 |  | 32 | 4.91 | 25.8 |  |  |\n|  |  | 32 | 16 | 16 |  | 16 | 5.01 | 25.4 |  | 58 |\n| (B) |  |  |  |  |  |  | 5.16 | 25.1 |  | 60 |\n|  |  | 2 |  |  |  |  | 6.11 | 23.7 |  | 36 |\n|  |  | 4 |  |  |  |  | 5.19 | 25.3 |  | 50 |\n|  |  | 8 |  |  |  | 32 | 4.88 | 25.5 |  | 80 |\n| (C) |  | 256 |  | 32 | 32 |  | 5.75 | 24.5 |  | 28 |\n|  |  | 1024 | 32 | 128 |  |  | 4.66 | 26.0 |  | 168 |\n|  |  | 1024 | 128 | 128 |  |  | 4.75 | 25.4 |  | 53 |\n| (D) |  |  | 0.0 | 0.2 |  |  | 5.77 | 24.6 |  |  |\n|  |  | 1024 |  |  |  |  | 4.95 | 25.5 |  | 25.3 |\n|  |  | 4096 |  | 0.0 |  |  | 4.67 | 25.3 |  | 25.7 |\n| (E) |  |  | 0.2 |  |  |  | 5.47 | 25.7 |  |  |\n| big | 6 | 1024 | 16 | 4096 | 0.3 | 300K | 4.33 | 26.4 |  | 213 |\n\nTable 3 rows (B), we observe that reducing the attention key size $d_k$ hurts model quality. This suggests that determining compatibility is not easy and that a more sophisticated compatibility function than dot product may be beneficial. We further observe in rows (C) and (D) that, as expected, bigger models are better, and dropout is very helpful in avoiding over-fitting. In row (E) we replace our sinusoidal positional encoding with learned positional embeddings, and observe nearly identical results to the base model.\n\n7 Conclusion\nIn this work, we presented the Transformer, the first sequence transduction model based entirely on attention, replacing the recurrent layers most commonly used in encoder-decoder architectures with multi-headed self-attention. For translation tasks, the Transformer can be trained significantly faster than architectures based on recurrent or convolutional layers. On both WMT 2014 English-to-German and WMT 2014 English-to-French translation tasks, we achieve a new state of the art. In the former task our best model outperforms even all previously reported ensembles.\nWe are excited about the future of attention-based models and plan to apply them to other tasks. We plan to extend the Transformer to problems involving input and output modalities other than text and to investigate local, restricted attention mechanisms to efficiently handle large inputs and outputs such as images, audio and video. Making generation less sequential is another research goals of ours.\"}{\"text\":\"\nReferences\n\n\\[1] Jimmy Lei Ba, Jamie Ryan Kiros, and Geoffrey E Hinton. Layer normalization. arXiv preprint arXiv:1607.06450, 2016.\n\n\\[2] Dzmitry Bahdanau, Kyunghyun Cho, and Yoshua Bengio. Neural machine translation by jointly learning to align and translate. CoRR, abs/1409.0473, 2014.\n\n\\[3] Denny Britz, Anna Goldie, Minh-Thang Luong, and Quoc V. Le. Massive exploration of neural machine translation architectures. CoRR, abs/1703.03906, 2017.\n\n\\[4] Jianpeng Cheng, Li Dong, and Mirella Lapata. Long short-term memory-networks for machine reading. arXiv preprint arXiv:1601.06733, 2016.\n\n\\[5] Kyunghyun Cho, Bart van Merrienboer, Caglar Gulcehre, Fethi Bougares, Holger Schwenk, and Yoshua Bengio. Learning phrase representations using rnn encoder-decoder for statistical machine translation. CoRR, abs/1406.1078, 2014.\n\n\\[6] Francois Chollet. Xception: Deep learning with depthwise separable convolutions. arXiv preprint arXiv:1610.02357, 2016.\n\n\\[7] Junyoung Chung, Çağlar Gülçehre, Kyunghyun Cho, and Yoshua Bengio. Empirical evaluation of gated recurrent neural networks on sequence modeling. CoRR, abs/1412.3555, 2014.\n\n\\[8] Jonas Gehring, Michael Auli, David Grangier, Denis Yarats, and Yann N. Dauphin. Convolutional sequence to sequence learning. arXiv preprint arXiv:1705.03122v2, 2017.\n\n\\[9] Alex Graves. Generating sequences with recurrent neural networks. arXiv preprint arXiv:1308.0850, 2013.\n\n\\[10] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. Deep residual learning for image recognition. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition, pages 770–778, 2016.\n\n\\[11] Sepp Hochreiter, Yoshua Bengio, Paolo Frasconi, and Jürgen Schmidhuber. Gradient flow in recurrent nets: the difficulty of learning long-term dependencies, 2001.\n\n\\[12] Sepp Hochreiter and Jürgen Schmidhuber. Long short-term memory. Neural computation, 9(8):1735–1780, 1997.\n\n\\[13] Rafal Jozefowicz, Oriol Vinyals, Mike Schuster, Noam Shazeer, and Yonghui Wu. Exploring the limits of language modeling. arXiv preprint arXiv:1602.02410, 2016.\n\n\\[14] Łukasz Kaiser and Ilya Sutskever. Neural GPUs learn algorithms. In International Conference on Learning Representations (ICLR), 2016.\n\n\\[15] Nal Kalchbrenner, Lasse Espeholt, Karen Simonyan, Aaron van den Oord, Alex Graves, and Ko-   ray Kavukcuoglu. Neural machine translation in linear time. arXiv preprint arXiv:1610.10099v2, 2017.\n\n\\[16] Yoon Kim, Carl Denton, Luong Hoang, and Alexander M. Rush. Structured attention networks. In International Conference on Learning Representations, 2017.\n\n\\[17] Diederik Kingma and Jimmy Ba. Adam: A method for stochastic optimization. In ICLR, 2015.\n\n\\[18] Oleksii Kuchaiev and Boris Ginsburg. Factorization tricks for LSTM networks. arXiv preprint arXiv:1703.10722, 2017.\n\n\\[19] Zhouhan Lin, Minwei Feng, Cicero Nogueira dos Santos, Mo Yu, Bing Xiang, Bowen Zhou, and Yoshua Bengio. A structured self- attentive sequence embedding. arXiv preprint arXiv:1703.03130, 2017.\n\n\\[20] Samy Bengio Łukasz Kaiser. Can active memory replace attention? In Advances in Neural Information Processing Systems, (NIPS), 2016.\n\"}{\"text\":\"\\\begin{enumerate}\n\\\\item\\\\emph{Introduction}\n\\\\item\\\\emph{Background: Ontology-based System}\n\\\\item\\\\emph{Problem Statement: Incomplete Definitions of}\n\\\\emph{Concepts in Knowledge Graphs}\n\\\\item\\\\emph{XML in nová foi Computers}\n\\\\item\\\\emph{Manifestation: Known Chíallenges and}\n\\\\emph{Problems in Handling Knowledge Graphs}\n\\\\item\\\\emph{Proposed Solution: Approach to}\n\\\\emph{Addressing Incomplete Definitions in}\n\\\\emph{Knowledge Graphs}\n\\\\end{enumerate}\n\n\\\begin{enumerate}\n\\\\item\\\\emph{Problem Identification:}\n\\\\item\\\\emph{Incompleteness of Knowledge Graphs:}\n\\\\item\\\\emph{Problem Definition}\n\\\\item\\\\emph{Scenarios:}\n    \\\begin{enumerate}\n    \\\\item\\\\emph{Concepts in Knowledge Graphs}\n    \\\\item\\\\emph{No clear identifiability of gaps in}\n\\\\emph{the Enabled System Knowledge}\n    \\\\item\\\\emph{Location Crazy Information searchBag}\n\\\\item\\\\item \\\\emph{Augmentation}\n    \\\\end{enumerate}\n\\\\item\\\\emph{Reasoning}\n\\\\item\\\\emph{Identification of Unknown Visual Habits\n\\\\emph{Utilization of Reduced interaction character_user\n\\\\item\\\\item Problem maintain all enabled sub concepts}\n\\\\item\\\\item Which row cannot facilitate into several signed}\n\\\\end{enumerate}\n\n\\\begin{enumerate}\n\\\\item\\\\emph{Responsible:}\n\\\\item\\\\emph{Defining the GR System env replicas Without\n\\\\emph{Contradictions}\n\\\\item\\\\emph{Approach strategies accomplishing proxy to action}\n       \\\\item Networks Mez transaction\n\\\\end{enumerate}\n\n\\\begin{enumerate}\n\\\\item\\\\emph{Measurement Asssets effective improvements\n\\\\emph{Introduction Source reference name feed04validate further feeding many}\n\\\\end{enumerate}\n\n\\\begin{enumerate}\n\\\\item\\\\emph{Experimental Methods Format supported passenger ad(Ntrack and is Differential specialization}\n\\\\end{enumerate}\n\n\\\begin{enumerate}\n\\\\item\\\\emph{topic-hypo Association Style Assignpus}\n\\\\end{enumerate}\n\n\\\begin{enumerate}\n\\\\item\\\\emph{CHECK}\n\\\\item\\\\emph{find evidence sound explanation donn Closed include sums}\n\\\\end{enumerate}\n\n\\\begin{enumerate}\n\\\\item\\\\emph{Scenario– and-default notch Hardware Cut-memory}\n\\\\end{enumerate}\n\n\\\begin{enumerate}\n\\\\item\\\\emph{Similar System C\"})"))