import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';

export default function PodcastPlayer() {
  return (
    <Card className="w-full max-w-2xl mx-auto mt-8">
      <CardHeader>
        <CardTitle className="text-2xl font-bold">XMRT DAO Podcast: Privacy, Mining, and Governance</CardTitle>
      </CardHeader>
      <CardContent>
        <audio controls className="w-full">
          <source src="/podcast.mp3" type="audio/mpeg" />
          Your browser does not support the audio element.
        </audio>
        <p className="text-sm text-muted-foreground mt-4">
          Listen to our latest podcast episode exploring the intersection of privacy, mobile Monero, and XMRT DAO governance.
        </p>
      </CardContent>
    </Card>
  );
}

