# LautrerWissen-Backend
This repository holds the backend and data import code for the project LautrerWissen

## About the project

What is happening with the construction site in my neighborhood? What are the particulate levels here? And were there
any decisions made at the last city council meeting that affect me? The people of Lautr are interested in their city and
especially in their immediate surroundings. With this project, we want to make it even easier for citizens to access
information that is important to them! Using QR codes in public spaces and, of course, web links, interested parties
should be able to access a website (a so-called dashboard) that summarizes important information for the respective
neighbourhood. This could be real-time data from air quality measurements, for example, or the aforementioned
resolutions from city council meetings. Photos, easy-to-understand maps, information texts and the graphical
presentation of data are all conceivable. The aim is to provide citizens with information that is important for their
everyday lives in the city in a simpler, more concrete and comprehensible way. The aim is to increase understanding and
interest in the importance of various city data.

## Backend component

The backend implementation for the project LautrerWissen is located in the folder /webapp. The backend is a Django Application with a RESTful-API and consists of the following Django apps:
- webapp: core backend logic
- lautrer_wissen: models, logic and viewsets for the specific data model available for Kaiserslautern
- frontend_config: parts of the frontend such as the configuration of the map sidebar can be configured here (e.g. groups, layer names, ordering, etc.)
- pipeline_manager: backend code for inspecting and executing data import pipelines for all dynamic datasets
