require 'net/http'
require 'json'
require 'uri'

class PerplexityClient
  BASE_URL = "https://api.perplexity.ai/chat/completions"

  def initialize(api_key = ENV['PERPLEXITY_API_KEY'])
    @api_key = api_key
  end

  def generate_article(title)
    uri = URI(BASE_URL)
    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl = true

    request = Net::HTTP::Post.new(uri)
    request["Authorization"] = "Bearer #{@api_key}"
    request["Content-Type"] = "application/json"
    request["Accept"] = "application/json"

    body = {
      model: "sonar-medium",
      messages: [
        {
          role: "system",
          content: "You are a helpful technical writer."
        },
        {
          role: "user",
          content: "Write a full technical blog article titled: #{title}. Include code examples if appropriate."
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
