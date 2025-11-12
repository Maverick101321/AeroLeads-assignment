# This file should ensure the existence of records required to run the application in every environment (production,
# development, test). The code here should be idempotent so that it can be executed at any point in every environment.
# The data can then be loaded with the bin/rails db:seed command (or created alongside the database with db:setup).
#
# Example:
#
#   ["Action", "Comedy", "Drama", "Horror"].each do |genre_name|
#     MovieGenre.find_or_create_by!(name: genre_name)
#   end

Contact.destroy_all
numbers = [
  "+9118001000001", "+9118001000002", "+9118001000003",
  "+9118001000004", "+9118001000005", "+9118001000006",
  "+9118001000007", "+9118001000008", "+9118001000009",
  "+9118001000010"
]
numbers.each do |num|
  Contact.create!(phone_number: num, status: "pending")
end
puts "Seeded #{Contact.count} contacts."
