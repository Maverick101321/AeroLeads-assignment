class BlogsController < ApplicationController
  def index
    @blogs = Blog.order(created_at: :desc)
  end

  def show
    @blog = Blog.find(params[:id])
  end

  def new
  end

  def create_multiple
    titles_param = params[:titles].to_s
    titles = titles_param.lines.map(&:strip).reject(&:blank?).first(10)

    if titles.empty?
      redirect_to blog_generate_path, alert: "Please enter at least one title."
      return
    end

    client = PerplexityClient.new(ENV["PERPLEXITY_API_KEY"])
    created_count = 0

    titles.each do |title|
      content = client.generate_article(title)
      if content.present?
        Blog.create(title: title, body: content)
        created_count += 1
      end
    end

    redirect_to blogs_path, notice: "Generated #{created_count} articles."
  end
end
