# Event-Item-Manager
A project I made after first learning how to apply databases to apps about a year ago in 2025. I updated it a little later to go from being localhost to a MongoDB Atlas server, meaning you don't have to download anything else for this to store your information.

This app lets you create an event, and create different items in the event, giving them a name, amount, and price. Using that information, it gives you a total cost of the event. The app also lets you delete events and items, and mark what items you have collected so far, giving another price calculation, being the cost remaining. The app uses MongoDB, giving a database where it stores the information, meaning that you can close the app, reopen it, and your event items will still be there. It works on a username system, where each username stores the information separately.

The way it uses MongoDB is through a personal MongoDB Atlas server, where it uses my connection string, and originally, it was localhost on your computer, but now you don't have to download MongoDB since it just asks for you to put a username to access your previous data.
