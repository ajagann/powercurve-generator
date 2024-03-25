#include <cstdlib>
#include <iostream>
#include <string>


int main() {
    // Start NGINX
    std::cout << "Starting NGINX..." << std::endl;
    const char* benchmarkCmd = "nginx -c nginx.conf";

    // Execute the shell function
    int result = std::system(benchmarkCmd);

    if (nginxResult != 0) {
        std::cerr << "Error starting NGINX" << std::endl;
        return 1;
    }

    // Make N queries to NGINX
    int numQueries = 5;
    for (int i = 0; i < numQueries; ++i) {
        // Perform HTTP request to NGINX
        std::string httpRequest = "curl http://localhost:80"; // Assuming NGINX is running on port 80
        std::cout << "Making request: " << httpRequest << std::endl;
        int requestResult = std::system(httpRequest.c_str());

        if (requestResult != 0) {
            std::cerr << "Error making request to NGINX" << std::endl;
        }
    }

    // Stop NGINX
    std::cout << "Stopping NGINX..." << std::endl;
    int nginxStopResult = std::system("nginx -s stop");

    if (nginxStopResult != 0) {
        std::cerr << "Error stopping NGINX" << std::endl;
        // You may want to handle this error accordingly
    }

    return 0;
}