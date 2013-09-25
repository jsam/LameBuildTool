#ifndef HEADER_SRC_APP_H_INCLUDED
#define HEADER_SRC_APP_H_INCLUDED

// TODO: include specified libraries

class App
{
 public:
  App(int &argc, char** argv);
  ~App();
  
  std::string getProjectName();
  std::string getProjectCodename();
  std::string getCopyrightYear();
  int getProjectMajorVersion();
  int getProjectMinorVersion();
  std::string getProjectVersion();

  std::string getProjectVendorID();
  std::string getProjectVendorName();
  std::string getProjectVendorURL();

  std::string getProjectID();
    
 private:
  void printHelpMessage();
  void printVersionMessage();
  void printApplicationIdentifier();

  static App* _instance;
  
  
};

#endif
