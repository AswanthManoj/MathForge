from sentence_transformers import SentenceTransformer, util

model = None
def load_model(model_name: str='all-MiniLM-L6-v2'):
    # This is a singleton now and each time it will not get loaded to memory as in the previous implementation
    global model
    if model is None:
        model = SentenceTransformer(model_name)
    return model

def check_similar_questions(existing_questions, new_questions, similarity_threshold=0.9):
    """
    Filters out semantically similar questions from new_questions based on existing_questions.

    Args:
        existing_questions (list): List of existing questions (strings).
        new_questions (list): List of new questions to check (strings).
        similarity_threshold (float): Cosine similarity threshold to consider questions similar.

    Returns:
        list: List of objects, each containing a removed question and a list of similar existing questions.
              Format: [{'question': 'removed question', 'similarTo': ['similar existing question 1', 'similar existing question 2', ...]}]
    """
    if not existing_questions:
        print("Warning: existing_questions list is empty. No questions will be filtered.")
        return []

    model = load_model()
    existing_embeddings = model.encode(existing_questions, convert_to_tensor=True)

    removed_questions = []

    for new_question in new_questions:
        new_embedding = model.encode(new_question, convert_to_tensor=True)

        cosine_scores = util.cos_sim(new_embedding, existing_embeddings)[0]

        similar_question_indices = [i for i, score in enumerate(cosine_scores) if score >= similarity_threshold]
        similar_questions = [existing_questions[i] for i in similar_question_indices]

        if similar_questions:
            removed_questions.append({
                "question": new_question,
                "similarTo": similar_questions
            })

    return removed_questions

if __name__ == '__main__':
    # Example Usage (for testing the core function directly)
    existing_questions_example = [
        "What is sin 30?",
        "Explain the Pythagorean theorem.",
        "Solve for x in 2x + 5 = 11."
    ]
    new_questions_example = [
        "What is the value of sin 30?",
        "Describe the Pythagorean theorem.",
        "Find the value of x in the equation 2x + 5 = 11.",
        "What is the capital of France?" # Dissimilar question
    ]

    removed_list = check_similar_questions(existing_questions_example, new_questions_example)
    print("Removed Questions (Example):")
    for removed_item in removed_list:
        print(removed_item)