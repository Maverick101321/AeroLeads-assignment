class ContactsController < ApplicationController
    def index
      @contacts = Contact.order(:id)
    end
  
    def create
        raw_numbers = params[:numbers].to_s.lines
    
        cleaned_numbers =
          raw_numbers
            .map { |line| normalize_phone(line) }
            .compact
            .uniq
            .first(100) # enforce “Paste up to 100 numbers”
    
        cleaned_numbers.each do |phone|
          Contact.create!(
            phone_number: phone,
            status: "pending",
            last_called_at: nil
          )
        end
    
        flash[:notice] = "Added #{cleaned_numbers.count} contacts."
        redirect_to contacts_path
      rescue ActiveRecord::RecordInvalid => e
        flash[:alert] = "Could not add contacts: #{e.message}"
        redirect_to contacts_path
      end
  
    private
  
    def normalize_phone(raw)
      return if raw.blank?
  
      trimmed = raw.strip
  
      # Preserve leading +, remove other non-digits.
      normalized =
        if trimmed.start_with?("+")
          "+" + trimmed[1..].gsub(/\D/, "")
        else
          trimmed.gsub(/\D/, "")
        end
  
      return if normalized.blank?
  
      # Prefix +91 for plain 10-digit Indian numbers without country code.
      if normalized.length == 10 && !normalized.start_with?("+")
        normalized = "+91#{normalized}"
      end
  
      normalized
    end
  end