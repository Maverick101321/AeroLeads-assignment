class Contact < ApplicationRecord
    has_many :call_logs, dependent: :destroy
  end  