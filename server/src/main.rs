//! gRPC server implementation

///module svc_storage generated from svc-storage.proto
#[cfg(not(tarpaulin_include))]
pub mod svc_devops_test {
    #![allow(unused_qualifications, missing_docs)]
    include!("grpc.rs");
}

use svc_devops_test::devops_test_rpc_server::{DevopsTestRpc, DevopsTestRpcServer};
use svc_devops_test::{QueryIsReady, ReadyResponse};
use tonic::{transport::Server, Request, Response, Status};

///Implementation of gRPC endpoints
#[derive(Debug, Default, Copy, Clone)]
pub struct DevopsTestImpl {}

#[tonic::async_trait]
impl DevopsTestRpc for DevopsTestImpl {
    /// Returns ready:true when service is available
    async fn is_ready(
        &self,
        _request: Request<QueryIsReady>,
    ) -> Result<Response<ReadyResponse>, Status> {
        let response = ReadyResponse { ready: true };
        Ok(Response::new(response))
    }
}

/// Adding one to a number
#[allow(dead_code)]
fn add_one_if_lt_ten(a: u32) -> u32 {
    match a {
        0..=9 => a + 1,
        _ => a,
    }
}

///Main entry point: starts gRPC Server on specified address and port
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // GRPC Server
    let grpc_port = std::env::var("DOCKER_PORT_GRPC")
        .unwrap_or_else(|_| "50051".to_string())
        .parse::<u16>()
        .unwrap_or(50051);

    let full_grpc_addr = format!("[::]:{}", grpc_port).parse()?;

    let (mut health_reporter, health_service) = tonic_health::server::health_reporter();
    let imp = DevopsTestImpl::default();
    health_reporter
        .set_serving::<DevopsTestRpcServer<DevopsTestImpl>>()
        .await;

    //start server
    println!("Starting gRPC server at: {}", full_grpc_addr);
    Server::builder()
        .add_service(health_service)
        .add_service(DevopsTestRpcServer::new(imp))
        .serve(full_grpc_addr)
        .await?;
    println!("gRPC server running at: {}", full_grpc_addr);

    println!("test!");

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ut_add_one_if_lt_ten() {
        let x = 10;
        assert_eq!(add_one_if_lt_ten(x), x)
    }
}
