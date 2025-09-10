import 'package:flutter/material.dart';
import 'package:graphql_flutter/graphql_flutter.dart';
import 'video_player_screen.dart';

class VideoListScreen extends StatelessWidget {
  const VideoListScreen({super.key});

  static const videosQuery = '''
    query Videos {
      videos {
        id
        title
        thumbnailUrl
        playbackUrl
      }
    }
  ''';

  static const saveVideoMutation = '''
    mutation SaveVideo(\$videoId: ID!) {
      saveVideo(videoId: \$videoId) {
        ok
      }
    }
  ''';

  @override
  Widget build(BuildContext context) {
    return Query(
      options: QueryOptions(document: gql(videosQuery)),
      builder: (result, {fetchMore, refetch}) {
        if (result.isLoading) {
          return const Center(child: CircularProgressIndicator());
        }
        
        if (result.hasException) {
          return Center(child: Text('Error: ${result.exception.toString()}'));
        }
        
        final videos = result.data?['videos'] as List<dynamic>? ?? [];
        
        return GridView.builder(
          padding: const EdgeInsets.all(16),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            childAspectRatio: 0.7,
            crossAxisSpacing: 16,
            mainAxisSpacing: 16,
          ),
          itemCount: videos.length,
          itemBuilder: (context, index) {
            final video = videos[index];
            return Card(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: GestureDetector(
                      onTap: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => VideoPlayerScreen(
                              videoId: video['id'],
                              title: video['title'],
                              playbackUrl: video['playbackUrl'],
                            ),
                          ),
                        );
                      },
                      child: Container(
                        width: double.infinity,
                        decoration: BoxDecoration(
                          image: DecorationImage(
                            image: NetworkImage(video['thumbnailUrl']),
                            fit: BoxFit.cover,
                          ),
                        ),
                      ),
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          video['title'],
                          style: const TextStyle(fontWeight: FontWeight.bold),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 8),
                        Mutation(
                          options: MutationOptions(
                            document: gql(saveVideoMutation),
                            onCompleted: (data) {
                              if (data?['saveVideo']?['ok'] == true) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(content: Text('Video saved to watchlist')),
                                );
                              }
                            },
                          ),
                          builder: (runMutation, result) {
                            return SizedBox(
                              width: double.infinity,
                              child: ElevatedButton.icon(
                                onPressed: result?.isLoading == true ? null : () {
                                  runMutation({'videoId': video['id']});
                                },
                                icon: const Icon(Icons.bookmark_add),
                                label: const Text('Save'),
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }
}


