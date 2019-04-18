resource "null_resource" "cluster" {
    # Changes to any instance of the cluster requires re-provisioning
      triggers = {
          cluster_instance_ids = "${var.region}"
      }
      triggers = {
          name = "app"
      }

}
