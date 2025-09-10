import 'package:flutter/material.dart';
import 'package:graphql_flutter/graphql_flutter.dart';
import 'video_player_screen.dart';

class WatchlistScreen extends StatelessWidget {
  const WatchlistScreen({super.key});

  static const savedVideosQuery = '''
    query SavedVideos {
      me {
        savedVideos {
          video {
            id
            title
            description
            jellyfinItemId
          }
        }
      }
    }
  ''';

  static const unsaveVideoMutation = '''
    mutation UnsaveVideo(\$videoId: ID!) {
      unsaveVideo(videoId: \$videoId) {
        ok
      }
    }
  ''';

  @override
  Widget build(BuildContext context) {
    return Query(
      options: QueryOptions(document: gql(savedVideosQuery)),
      builder: (result, {fetchMore, refetch}) {
        if (result.isLoading) {
          return const Center(child: CircularProgressIndicator());
        }
        
        if (result.hasException) {
          return Center(child: Text('Error: ${result.exception.toString()}'));
        }
        
        final savedVideos = result.data?['me']?['savedVideos'] as List<dynamic>? ?? [];
        
        if (savedVideos.isEmpty) {
          return const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.bookmark_border, size: 64, color: Colors.grey),
                SizedBox(height: 16),
                Text('No saved videos yet', style: TextStyle(fontSize: 18, color: Colors.grey)),
              ],
            ),
          );
        }
        
        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: savedVideos.length,
          itemBuilder: (context, index) {
            final item = savedVideos[index];
            final video = item['video'];
            final videoId = video['jellyfinItemId'] ?? video['id'];
            
            return Card(
              margin: const EdgeInsets.only(bottom: 16),
              child: ListTile(
                title: Text(video['title']),
                subtitle: Text(video['description'] ?? ''),
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.play_arrow),
                      onPressed: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => VideoPlayerScreen(
                              videoId: videoId,
                              title: video['title'],
                              playbackUrl: '/stream/$videoId/master.m3u8', // This would be fetched from GraphQL
                            ),
                          ),
                        );
                      },
                    ),
                    Mutation(
                      options: MutationOptions(
                        document: gql(unsaveVideoMutation),
                        onCompleted: (data) {
                          if (data?['unsaveVideo']?['ok'] == true) {
                            refetch!();
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('Removed from watchlist')),
                            );
                          }
                        },
                      ),
                      builder: (runMutation, result) {
                        return IconButton(
                          icon: const Icon(Icons.bookmark_remove),
                          onPressed: result?.isLoading == true ? null : () {
                            runMutation({'videoId': videoId});
                          },
                        );
                      },
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }
}


