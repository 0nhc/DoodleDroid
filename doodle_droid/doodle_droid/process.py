import rclpy
import rclpy.parameter
from rclpy.node import Node
import rclpy.time

from sensor_msgs.msg import CompressedImage
from std_srvs.srv import Empty
from cv_bridge import CvBridge
import cv2 as cv
from doodle_droid.linedraw.linedraw import *
from std_msgs.msg import String
import json


class ImageProcessingNode(Node):
    def __init__(self):
        super().__init__('image_processing_node')

        self.image_sub = self.create_subscription(CompressedImage, '/image_raw/compressed', self.get_image_callback, 10)
        self.take_picture_service = self.create_service(Empty, '/take_picture', self.capture_image)
        self.processed_image_pub = self.create_publisher(String, '/new_image', 10)
        self.current_image = None
        self.absolute_path = '/home/harrison-bounds/ws/ES_HW/doodle_droid/src/DoodleDroid/doodle_droid/doodle_droid/images/output.jpg'
        self.bridge = CvBridge()
        
    def get_image_callback(self, msg):
        self.current_image = msg
    
    def capture_image(self, request, response):
        cv_image = self.bridge.compressed_imgmsg_to_cv2(self.current_image, desired_encoding='passthrough')
        self.get_logger().info(f"cv image type: {type(cv_image)}")
        lined_image = doodle_droid.linedraw.linedraw.sketch(cv_image)
        self.get_logger().info(f"Number of strokes: {len(lined_image)} ")
        self.get_logger().info("Finished processing")
        
        json_data = json.dumps(lined_image)
        msg = String()
        msg.data = json_data
        self.processed_image_pub.publish(msg)
                
        return response

def main(args=None):
    rclpy.init(args=args)
    node = ImageProcessingNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    import sys
    main(sys.argv)