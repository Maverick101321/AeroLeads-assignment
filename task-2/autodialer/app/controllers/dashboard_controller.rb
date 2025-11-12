class DashboardController < ApplicationController
  def index
    @contacts = Contact.order(:id)
  end
end