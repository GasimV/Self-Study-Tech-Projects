import torch
import tiktoken
from tokenizer import SimpleTokenizerV1, SimpleTokenizerV2, create_vocab_from_text
from dataloader import create_dataloader_v1
from attention import (
    SelfAttention_v1, 
    SelfAttention_v2, 
    CausalAttention, 
    MultiHeadAttention
)


def main():
    # Check GPU availability
    print("GPU is available:", torch.cuda.is_available())
    
    # Load text data
    with open("the-verdict.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()
    
    print("Total number of characters:", len(raw_text))
    print(raw_text[:99])
    
    # Create vocabulary and tokenizer
    vocab = create_vocab_from_text(raw_text)
    print(f"Vocabulary size: {len(vocab)}")
    
    # Initialize tokenizer
    tokenizer = SimpleTokenizerV2(vocab)
    
    # Test tokenization
    text = "Hello, do you like tea? <|endoftext|> In the sunlit terraces of the palace."
    encoded = tokenizer.encode(text)
    print(f"Encoded: {encoded}")
    decoded = tokenizer.decode(encoded)
    print(f"Decoded: {decoded}")
    
    # Use BPE tokenizer
    bpe_tokenizer = tiktoken.get_encoding("gpt2")
    
    # Create dataloader
    max_length = 4
    dataloader = create_dataloader_v1(
        raw_text, 
        batch_size=8, 
        max_length=max_length,
        stride=max_length, 
        shuffle=False
    )
    
    # Get batch
    data_iter = iter(dataloader)
    inputs, targets = next(data_iter)
    print("Inputs shape:", inputs.shape)
    print("Targets shape:", targets.shape)
    
    # Create embeddings
    vocab_size = 50257
    output_dim = 256
    token_embedding_layer = torch.nn.Embedding(vocab_size, output_dim)
    pos_embedding_layer = torch.nn.Embedding(max_length, output_dim)
    
    token_embeddings = token_embedding_layer(inputs)
    pos_embeddings = pos_embedding_layer(torch.arange(max_length))
    input_embeddings = token_embeddings + pos_embeddings
    print("Input embeddings shape:", input_embeddings.shape)
    
    # Test attention mechanisms
    batch = torch.stack((input_embeddings[0:2], input_embeddings[0:2]), dim=0)
    
    # Test CausalAttention
    torch.manual_seed(123)
    context_length = batch.shape[1]
    d_in = batch.shape[2]
    d_out = 2
    ca = CausalAttention(d_in, d_out, context_length, 0.0)
    context_vecs = ca(batch)
    print("Causal Attention output shape:", context_vecs.shape)
    
    # Test MultiHeadAttention
    torch.manual_seed(123)
    mha = MultiHeadAttention(d_in, d_out, context_length, 0.0, num_heads=2)
    context_vecs = mha(batch)
    print("Multi-Head Attention output shape:", context_vecs.shape)
    print("Multi-Head Attention output:", context_vecs)


if __name__ == "__main__":
    main()
