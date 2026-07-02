import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Dict
import math
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)


class TokenPredictor:
    def __init__(self, model_name: str):
        # Configure the client to route through OpenRouter
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_PAID_API_KEY"),
        )
        self.model_name = model_name

    def predict_tokens(self, prompt: str, max_tokens: int = 100) -> List[Dict]:
        """
        Generate text token by token and track prediction probabilities.
        Returns list of predictions with top token and alternatives.
        """
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0,  # Use temperature 0 for deterministic output
            logprobs=True,
            seed=42,
            top_logprobs=3,  # Get top 3 token predictions
            stream=True,  # Stream the response
        )

        predictions = []
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                
                if chunk.choices[0].logprobs and chunk.choices[0].logprobs.content:
                    logprobs = chunk.choices[0].logprobs.content[0].top_logprobs
                    logprob_dict = {item.token: item.logprob for item in logprobs}

                    top_token = token
                    top_prob = logprob_dict.get(token, 0.0) 

                    alternatives = []
                    for alt_token, alt_prob in logprob_dict.items():
                        if alt_token != token:
                            alternatives.append((alt_token, math.exp(alt_prob)))
                    alternatives.sort(key=lambda x: x[1], reverse=True)

                    prediction = {
                        "token": top_token,
                        "probability": math.exp(top_prob) if top_prob != 0.0 else 1.0,
                        "alternatives": alternatives[:2],
                    }
                    predictions.append(prediction)

        return predictions


def create_token_graph(model_name: str, predictions: List[Dict]) -> nx.DiGraph:
    G = nx.DiGraph()
    G.add_node("START", token=model_name, prob="START", color="lightgreen", size=4000)

    for i, pred in enumerate(predictions):
        token_id = f"t{i}"
        G.add_node(
            token_id,
            token=pred["token"],
            prob=f"{pred['probability'] * 100:.1f}%",
            color="lightblue",
            size=6000,
        )

        if i == 0:
            G.add_edge("START", token_id)
        else:
            G.add_edge(f"t{i - 1}", token_id)

    last_id = None
    for i, pred in enumerate(predictions):
        parent_token = "START" if i == 0 else f"t{i - 1}"

        for j, (alt_token, alt_prob) in enumerate(pred["alternatives"]):
            alt_id = f"t{i}_alt{j}"
            G.add_node(
                alt_id, token=alt_token, prob=f"{alt_prob * 100:.1f}%", color="lightgray", size=6000
            )
            G.add_edge(parent_token, alt_id)
            last_id = parent_token

    G.add_node("END", token="END", prob="100%", color="red", size=6000)
    G.add_edge(last_id, "END")

    return G


def visualize_predictions(G: nx.DiGraph, figsize=(14, 80)):
    plt.figure(figsize=figsize)
    pos = {}
    spacing_y = 5
    spacing_x = 5

    main_nodes = [n for n in G.nodes() if "_alt" not in n]
    for i, node in enumerate(main_nodes):
        pos[node] = (0, -i * spacing_y)

    for node in G.nodes():
        if "_alt" in node:
            main_token = node.split("_")[0]
            alt_num = int(node.split("_alt")[1])
            if main_token in pos:
                x_offset = -spacing_x if alt_num == 0 else spacing_x
                pos[node] = (x_offset, pos[main_token][1] + 0.05)

    node_colors = [G.nodes[node]["color"] for node in G.nodes()]
    node_sizes = [G.nodes[node]["size"] for node in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes)
    nx.draw_networkx_edges(G, pos, edge_color="gray", arrows=True, arrowsize=20, alpha=0.7)

    labels = {node: f"{G.nodes[node]['token']}\n{G.nodes[node]['prob']}" for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=14)

    plt.title("Token prediction.")
    plt.axis("off")

    margin = 8
    x_values = [x for x, y in pos.values()]
    y_values = [y for x, y in pos.values()]
    plt.xlim(min(x_values) - margin, max(x_values) + margin)
    plt.ylim(min(y_values) - margin, max(y_values) + margin)

    return plt