from rest_framework import serializers
from core.models import Sermon

class SermonSerializer(serializers.ModelSerializer):
    assembly_name = serializers.CharField(source='assembly.name', read_only=True)
    
    class Meta:
        model = Sermon
        fields = [
            'id',
            'assembly',
            'assembly_name',
            'title', 
            'preacher',
            'bible_passage',
            'sermon_date',
            'audio_file',
            'video_url',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']