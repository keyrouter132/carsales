from flask import Flask, request, jsonify
import matplotlib.pyplot as plt
import seaborn as sns #adjust the styling
import pandas as pd
import pandas as pd
import logging

# Initialize the Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Define the API route for analysis
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Log the incoming request data
        app.logger.debug(f"Incoming request data: {request.json}")
        
        # Get JSON data from the request
        data = request.json
        
        # Check if data is None or empty
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Convert JSON data to a Pandas DataFrame
        df = pd.DataFrame(data)
        
        # Perform your analysis here
        # Example: Calculate summary statistics
        result = df.describe().to_dict()
        
        car_details = pd.read_csv('car_details_df.csv')
        price_cardetails = pd.read_csv('price_cardetails_df.csv')

        #1. Most common car brands
        top_brands = car_details['Brand'].value_counts().head(5)
        print(top_brands)

        #2.Brand and its models
        brand_model_df = car_details.groupby("Brand")["Model"].unique().reset_index()
        for index, row in brand_model_df.iterrows():
            print(f"Brand: {row['Brand']}")
            print(f"Models: {', '.join(row['Model'])}")
            print("-" * 50)

        #3.Brand and its Transmission Types
        brand_transmission_df = car_details.groupby("Brand")["Transmission"].unique().reset_index()
        for index, row in brand_transmission_df.iterrows():
            print(f"Brand: {row['Brand']}")
            print(f"Transmission Types: {', '.join(row['Transmission'])}")
            print("-" * 50)

        # 4.Most popular brand in each location
        popular_brands_by_location = car_details.groupby(["Location", "Brand"]).size().reset_index(name="Count")
        popular_brands = popular_brands_by_location.loc[popular_brands_by_location.groupby("Location")["Count"].idxmax()]

        for index, row in popular_brands.iterrows():
            print(f"Location: {row['Location']}")
            print(f"Most Popular Brand: {row['Brand']} (Listings: {row['Count']})")
            print("-" * 50)

        # 5. Average mileage per fuel type
        avg_mileage = car_details.groupby('Fuel_Type')['Mileage_km'].mean()
        print(avg_mileage)

        # 6.Basic Statistical Summary
        print("\nPrice Dataset Description:")
        print(price_cardetails.describe())
        print("\nCar Details Dataset Description:")
        print(car_details.describe())

        # 7. Most common transmission type in recent years
        recent_transmission = car_details[car_details['Year'] >= 2020]['Transmission'].value_counts()
        print(recent_transmission)

        #8.Location with most cars listed
        top_locations = car_details['Location'].value_counts().head(10)
        plt.figure(figsize=(10,5))

        sns.barplot(x=top_locations.index, y=top_locations.values,hue=top_locations.index ,palette='cividis')
        plt.title('Top 10 Locations with Most Cars Listed')
        plt.xlabel('Location')
        plt.ylabel('Count')
        plt.ylim(4300, max(top_locations.values) + 10)
        plt.xticks(rotation=45)
        plt.show()

        # 9. Count of Cars by Fuel Type
        merged_df = pd.merge(car_details, price_cardetails, on='Car_ID', how='inner')
        fuel_counts = merged_df["Fuel_Type"].value_counts()
        print(fuel_counts)

        # 10.Common price range for each car model
        merged_df.groupby("Model")["Price_USD"].describe()
        #25% to 75% (Interquartile Range) → Common price range
        #min and max → Price extremes
        #50% (median) → Most common price

        #11.most expensive car models
        merged_df.groupby("Model")["Price_USD"].mean().sort_values(ascending=False).head(10)

        #12.correlation between car age and price
        merged_df["car_Age"]= 2024 - merged_df["Year"]
        merged_df[["car_Age","Price_USD"]].corr()

        #13.avg price ofautomatic vs manual cars
        merged_df.groupby("Transmission")["Price_USD"].mean()

        #14.top 5 brands with highest resale values
        resale_values=merged_df.groupby("Brand")["Price_USD"].median().sort_values(ascending=False)
        print(resale_values)

        #15.Engine size vs average price
        eng= merged_df.groupby("Engine_cc")["Price_USD"].mean()
        plt.ylim(76000, max(eng.values) + 200)
        sns.barplot(x="Engine_cc", y="Price_USD", data=merged_df, palette='cividis', hue="Engine_cc", legend=False)
        plt.title("Engine Size vs. Average Price")
        plt.show()

        #16.Average Resale Value by Fuel Type
        resale_values = merged_df.groupby("Fuel_Type")["Price_USD"].median().sort_values(ascending=False)

        # Plot the bar chart
        plt.figure(figsize=(10,5))
        sns.barplot(x=resale_values.index, y=resale_values.values, palette="cividis", hue=resale_values.index, legend=False)
        plt.title("Average Resale Value by Fuel Type")
        plt.xlabel("Fuel Type")
        plt.ylabel("Median Resale Price (USD)")
        plt.xticks(rotation=45)
        plt.ylim(76500, max(resale_values.values) + 200)
        plt.show()

        #17.avg price by Car Brand
        price_by_brand = merged_df.groupby("Brand")["Price_USD"].mean().sort_values(ascending=False)

        plt.figure(figsize=(12, 6))
        sns.barplot(x=price_by_brand.index, y=price_by_brand.values, palette="cividis",hue=price_by_brand.index)

        # Customize the plot
        plt.title("Average Price by Car Brand", fontsize=14)
        plt.xlabel("Car Brand", fontsize=12)
        plt.ylabel("Average Price (USD)", fontsize=12)
        plt.xticks(rotation=45)  # Rotate labels for better readability
        plt.ylim(76500, max(price_by_brand.values) + 200)
        plt.show()

        #18..TransmissionType vs Number of Cars
        transmission_counts = merged_df["Transmission"].value_counts().reset_index()
        transmission_counts.columns = ["Transmission Type", "Number of Cars"]

        plt.figure(figsize=(8, 5))
        sns.barplot(x="Transmission Type", y="Number of Cars", data=transmission_counts, palette="cividis", hue="Transmission Type",
            legend=False)
        plt.title("Count of Cars Based on Transmission Type" )
        plt.xlabel("Transmission Type")
        plt.ylabel("Number of Cars")
        plt.ylim(34000, transmission_counts["Number of Cars"].max() + 200)
        plt.show()

        #19.Depreciation: Average Price of Cars by Age
        merged_df["Car_Age"] = 2024 - merged_df["Year"]
        avg_price_by_age = merged_df.groupby("Car_Age")["Price_USD"].mean().reset_index()
        plt.figure(figsize=(10, 5))
        sns.barplot(x="Car_Age", y="Price_USD", data=avg_price_by_age, palette="cividis",hue="Car_Age",legend=False)
        plt.title("Depreciation: Average Price of Cars by Age")
        plt.xlabel("Car Age (Years)")
        plt.ylabel("Average Price (USD)")
        plt.xticks(rotation=45)
        plt.ylim(74000, avg_price_by_age["Price_USD"].max() + 5000)
        plt.show()
        #shows how car prices decrease as they get older
        #Helps understand which age range has the best resale value.

        #20.Car Brands with the Best Mileage-to-Price Ratio
        merged_df["Mileage_to_Price"] = merged_df["Mileage_km"] / merged_df["Price_USD"].replace(0, 1)
        # (replaces Price_USD = 0 with 1 to avoid division by zero errors)
        # Group by brand and calculate the average mileage-to-price ratio
        brand_mileage_price_ratio = merged_df.groupby("Brand")["Mileage_to_Price"].mean().reset_index()
        # Sort values in descending order to highlight the best brands
        brand_mileage_price_ratio = brand_mileage_price_ratio.sort_values(by="Mileage_to_Price", ascending=False).head(10)

        plt.figure(figsize=(12, 6))
        sns.barplot(x="Brand", y="Mileage_to_Price", data=brand_mileage_price_ratio, palette="cividis",hue="Brand",legend=False)

        plt.title("Car Brands with the Best Mileage-to-Price Ratio")
        plt.xlabel("Car Brand")
        plt.ylabel("Mileage per Unit Price")
        plt.xticks(rotation=45)
        plt.ylim(3.5, brand_mileage_price_ratio["Mileage_to_Price"].max() + 0.01)
        plt.show()
        print(brand_mileage_price_ratio)
        #Divides mileage (Mileage_km) by price (Price_USD) to calculate how many kilometers a car can run per unit price.

        #21.No of cars sold each year
        yearly_sales = car_details["Year"].value_counts().reset_index()
        yearly_sales.columns = ["Year", "Number of Listings"]
        yearly_sales = yearly_sales.sort_values("Year")  # Sort by year

        plt.figure(figsize=(10, 5))
        sns.barplot(x="Year", y="Number of Listings", data=yearly_sales, palette="cividis",hue="Year",legend=False)
        plt.title("Number of Cars Sold Each Year")
        plt.xlabel("Year")
        plt.ylabel("Number of Listings")
        plt.xticks(rotation=45)

        plt.ylim(3400, max(yearly_sales["Number of Listings"]) + 50)
        plt.show()

        #22.Price Trends Over Years
        merged_df["Car_Age"] = 2024 - merged_df["Year"]
        age_price = merged_df.groupby("Car_Age")["Price_USD"].mean().reset_index()

        plt.figure(figsize=(10, 5))
        sns.lineplot(x="Car_Age", y="Price_USD", data=age_price, marker="o", color="green")
        plt.title("Depreciation: Average Price of Cars by Age")
        plt.xlabel("Car Age (Years)")
        plt.ylabel("Average Price (USD)")
        plt.grid(True)
        plt.show()

        #23.ev in each location
        ev_cars = car_details[car_details["Fuel_Type"].str.contains("Electric", case=False, na=False)]
        # Count EV usage by state (Location)
        ev_by_state = ev_cars["Location"].value_counts()
        plt.figure(figsize=(8, 8))
        plt.pie(ev_by_state, labels=ev_by_state.index, autopct='%1.1f%%',colors=sns.color_palette("colorblind")  # Seaborn's colorblind-safe palette
        )
        plt.title("EV Vehicles Distribution by State")
        plt.show()

        #24.Transmission type in each location
        transmission_by_location = car_details.groupby(["Location", "Transmission"]).size().reset_index(name="Count")

        plt.figure(figsize=(14, 6))
        sns.barplot(x="Location", y="Count", hue="Transmission", data=transmission_by_location, palette="cividis")

        # Graph styling
        plt.title("Transmission Types in Each Location")
        plt.xlabel("Location")
        plt.ylabel("Number of Cars")
        plt.xticks(rotation=45)
        plt.ylim(400, transmission_by_location["Count"].max() + 100)
        plt.legend(title="Transmission Type")
        plt.show()

        #25.EV listing by year
        ev_cars = car_details[car_details["Fuel_Type"].str.contains("Electric", case=False, na=False)]

        # Count EV usage by Year
        ev_by_year = ev_cars["Year"].value_counts().sort_index()
        plt.figure(figsize=(12, 6))
        sns.barplot(x=ev_by_year.index, y=ev_by_year.values, palette="cividis",hue=ev_by_year.index,  # ✅ Assign hue
            legend=False )

        plt.title("Electric Vehicles (EV) Listings by Year")
        plt.xlabel("Year")
        plt.ylabel("Number of EV Listings")
        plt.xticks(rotation=45)
        plt.ylim(300, ev_by_year.max() + 50)  # Adds buffer to the top(ensures that the tallest bar in the plot doesn’t touch the top edge.)
        plt.show()

        # Return the result as JSON
        return jsonify(result)
    
    except Exception as e:
        # Log the error
        app.logger.error(f"Error: {str(e)}")
        # Handle errors
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
