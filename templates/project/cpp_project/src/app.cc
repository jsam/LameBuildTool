#include <iostream>
#include <stdexcept>
#include "app.h"
#include "config.h"


App::App(int &argc, char** argv)
{
  if ( _instance )
    {
      throw std::runtime_error("Only one application instance is allowed.");
    }

  // Set singleton instance to this
  _instance = this;

  // TODO: Configure logging mechanism
  
  // TODO: Parse command line options
  
};


App::~App()
{}


std::string App::getProjectName()
{
  return APPLICATION_NAME;
}


std::string App::getProjectCodename()
{
  return APPLICATION_CODENAME;
}


int App::getProjectMajorVersion()
{
  return APPLICATION_VERSION_MAJOR;
}

int App::getProjectMinorVersion()
{
  return APPLICATION_VERSION_MINOR;
}

std::string App::getProjectVersion()
{
  return APPLICATION_VERSION_MAJOR + "." + APPLICATION_VERSION_MINOR;
}


std::string App::getProjectVendorID()
{
  return APPLICATION_VENDOR_ID;
}


std::string App::getProjectVendorName()
{
  return APPLICATION_VENDOR_NAME;
}


std::string App::getProjectVendorURL()
{
  return APPLICATION_VENDOR_URL;
}


std::string App::getProjectID()
{
  return APPLICATION_ID;
}




void App::printHelpMessage()
{
  // TODO:
}


void App::printVersionMessage()
{
  // TODO:
}


void App::printApplicationIdentifier()
{
  std::cout << getProjectID() << std::endl;
}

App* App::_instance = 0;
