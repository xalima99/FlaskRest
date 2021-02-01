from ressources.ma import ma

class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id', 'planet_name', 'planet_type', 'home_start', 'mass', 'radius', 'distance')


planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)