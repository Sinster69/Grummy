from openai import AzureOpenAI
from django.conf import settings
from django.core.cache import cache

client = AzureOpenAI(
    api_key=settings.AZURE_API_KEY,
    api_version="2024-02-15-preview",
    azure_endpoint=settings.AZURE_ENDPOINT,
)


def get_ai_suggestions(title, description):
    cache_key = f"ai_{title}_{description}"

    # ✅ Check cache first
    cached = cache.get(cache_key)
    if cached:
        print("⚡ AI CACHE HIT")
        return cached

    print("❌ AI CACHE MISS")

    prompt = f"""
    Task: {title}
    Description: {description}

    Suggest better ways to complete this delivery efficiently.
    """

    response = client.chat.completions.create(
        model=settings.AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "You are a logistics expert."},
            {"role": "user", "content": prompt},
        ],
    )

    result = response.choices[0].message.content

    # ✅ Store in cache
    cache.set(cache_key, result, timeout=300)

    return result
