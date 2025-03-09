from links.user_input_link import UserInputLinkConfig

config_data = {
    "name": "Initial User Inputs",
    "type": "user_input",
    "inputs": {
         "Inspiration": {
              "type": "string",
              "description": "Provide some inspiration for the ice cream flavor.",
              "required": True,
              "default": "vanilla"
         },
         "Demographic": {
              "type": "string",
              "description": "Describe who you expect to be interested in this flavor.",
              "required": True,
              "default": "teenagers"
         }
    }
}

config = UserInputLinkConfig(**config_data)

# Programmatically set the value of "Inspiration"
config.inputs["Inspiration"]["value"] = "Strawberry"

# Retrieve the value of "Inspiration"
inspiration_value = config.inputs["Inspiration"].get("value")
print("Inspiration value:", inspiration_value)

print(config)

# Access the 'Inspiration' field
inspiration_field = config.inputs.get("Inspiration", {})

# Look at the 'required' property and the 'type'
print("Inspiration required:", inspiration_field.get("required"))
print("Inspiration type:", inspiration_field.get("type"))
