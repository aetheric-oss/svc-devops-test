//! Client Library: Client Functions, Structs, Traits
#![allow(unused_qualifications)]
include!("grpc.rs");

use super::*;

#[cfg(not(feature = "stub_client"))]
use lib_common::grpc::ClientConnect;
use lib_common::grpc::{Client, GrpcClient};
use rpc_service_client::RpcServiceClient;
/// GrpcClient implementation of the RpcServiceClient
pub type DevopsTestClient = GrpcClient<RpcServiceClient<Channel>>;

cfg_if::cfg_if! {
    if #[cfg(feature = "stub_backends")] {
        use svc_devops_test::grpc::server::{RpcServiceServer, ServerImpl};
        lib_common::grpc_mock_client!(RpcServiceClient, RpcServiceServer, ServerImpl);
        super::log_macros!("grpc", "app::client::mock::devops_test");
    } else {
        lib_common::grpc_client!(RpcServiceClient);
        super::log_macros!("grpc", "app::client::devops_test");
    }
}

#[cfg(not(feature = "stub_client"))]
#[async_trait]
impl crate::service::Client<RpcServiceClient<Channel>> for DevopsTestClient {
    type ReadyRequest = ReadyRequest;
    type ReadyResponse = ReadyResponse;

    async fn is_ready(
        &self,
        request: Self::ReadyRequest,
    ) -> Result<tonic::Response<Self::ReadyResponse>, tonic::Status> {
        grpc_info!("{} client.", self.get_name());
        grpc_debug!("request: {:?}", request);
        self.get_client().await?.is_ready(request).await
    }
}

#[cfg(feature = "stub_client")]
#[async_trait]
impl crate::service::Client<RpcServiceClient<Channel>> for DevopsTestClient {
    type ReadyRequest = ReadyRequest;
    type ReadyResponse = ReadyResponse;

    async fn is_ready(
        &self,
        request: Self::ReadyRequest,
    ) -> Result<tonic::Response<Self::ReadyResponse>, tonic::Status> {
        grpc_warn!("(MOCK) {} client.", self.get_name());
        grpc_debug!("(MOCK) request: {:?}", request);
        Ok(tonic::Response::new(ReadyResponse { ready: true }))
    }
}

#[cfg(test)]
mod tests {
    use crate::service::Client as ServiceClient;

    use super::*;

    #[tokio::test]
    #[cfg(not(feature = "stub_client"))]
    async fn test_client_connect() {
        let name = "devops_test";
        let (server_host, server_port) =
            lib_common::grpc::get_endpoint_from_env("SERVER_HOSTNAME", "SERVER_PORT_GRPC");

        let client: DevopsTestClient = GrpcClient::new_client(&server_host, server_port, name);
        assert_eq!(client.get_name(), name);

        let connection = client.get_client().await;
        println!("{:?}", connection);
        assert!(connection.is_ok());
    }

    #[tokio::test]
    async fn test_client_is_ready_request() {
        let name = "devops_test";
        let (server_host, server_port) =
            lib_common::grpc::get_endpoint_from_env("SERVER_HOSTNAME", "SERVER_PORT_GRPC");

        let client: DevopsTestClient = GrpcClient::new_client(&server_host, server_port, name);
        assert_eq!(client.get_name(), name);

        let result = client.is_ready(ReadyRequest {}).await;
        println!("{:?}", result);
        assert!(result.is_ok());
        assert_eq!(result.unwrap().into_inner().ready, true);
    }
}
