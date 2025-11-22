require 'net/http'
require 'json'
require 'uri'
require 'openssl'

class PerplexityClient
  BASE_URL = "https://api.perplexity.ai/chat/completions"

  def initialize(api_key = ENV['PERPLEXITY_API_KEY'])
    @api_key = api_key
  end

  def generate_article(title)
    uri = URI(BASE_URL)
    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl = true
    http.verify_mode = OpenSSL::SSL::VERIFY_NONE # Bypass SSL certificate verification issues

    request = Net::HTTP::Post.new(uri)
    request["Authorization"] = "Bearer #{@api_key}"
    request["Content-Type"] = "application/json"
    request["Accept"] = "application/json"

    body = {
      model: "sonar-pro",
      messages: [
        {
          role: "system",
          content: "You are a helpful technical writer."
        },
        {
          role: "user",
          content: "Write a full technical blog article titled: '#{title}'.
          
          Requirements:
          1. Output strictly in valid HTML format (no markdown backticks, no ```html wrapper).
          2. Use <h2>, <h3>, <p>, <ul>, <li>, <code>, <pre> tags for structure.
          3. Do NOT use citations like [1], [2], etc. Remove them completely.
          4. Include 2-3 relevant placeholder images using <img src='https://placehold.co/600x400?text=Topic+Image' alt='Topic Description' /> but replace the text param with something relevant to the section.
          5. If appropriate, include a mermaid.js diagram description in a <pre class='mermaid'> block or a code example.
          6. Make it look professional and ready to publish."
        }
      ]
    }

    request.body = body.to_json

    response = http.request(request)

    if response.code.to_i == 200
      json_response = JSON.parse(response.body)
      json_response.dig("choices", 0, "message", "content")
    else
      Rails.logger.error "Perplexity API Error: #{response.code} - #{response.body}"
      nil
    end
  rescue StandardError => e
    Rails.logger.error "Perplexity Client Exception: #{e.message}"
    nil
  end
end
