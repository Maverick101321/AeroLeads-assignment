require "twilio-ruby"

class CallsController < ApplicationController
  skip_before_action :verify_authenticity_token

  def start_batch
    first = Contact.where(status: "pending").order(:id).first
    if first
      DialNextJob.perform_later(first.id)
      render plain: "Dialing started with #{first.phone_number}"
    else
      render plain: "No pending contacts."
    end
  end

  def start_prompt
    prompt = params[:prompt].to_s
    # Extract phone number: 10-13 digits, optionally with +
    match = prompt.match(/\+?\d{10,13}/)

    unless match
      redirect_to root_path, alert: "Could not find a phone number in your prompt."
      return
    end

    phone_number = match[0]

    # Normalize: if 10 digits and no +, prefix +91
    if phone_number.match?(/^\d{10}$/)
      phone_number = "+91#{phone_number}"
    end

    # Create or reuse contact
    contact = Contact.find_or_initialize_by(phone_number: phone_number)
    contact.status = "pending"
    contact.save!

    # Enqueue job
    DialNextJob.perform_later(contact.id)

    redirect_to root_path, notice: "Calling #{phone_number} based on your prompt."
  end

  def twiml
    response = Twilio::TwiML::VoiceResponse.new
    response.say(
      message: "Hello, this is a test call from your autodialer. Have a nice day.",
      voice: "Polly.Aditi"
    )
    render xml: response.to_xml
  end

  # Twilio calls this URL when call finishes
  def status
    sid     = params["CallSid"]
    status  = params["CallStatus"]
    contact = Contact.find_by(id: params["contact_id"])
    return head :ok unless contact

    contact.update(status: status, last_called_at: Time.current)

    # queue next pending contact
    next_contact = Contact.where(status: "pending").order(:id).first
    DialNextJob.perform_later(next_contact.id) if next_contact

    head :ok
  end
end
